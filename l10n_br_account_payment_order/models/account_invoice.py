#    @author Danimar Ribeiro <danimaribeiro@gmail.com>
# © 2012 KMEE INFORMATICA LTDA
#   @author Luis Felipe Mileo <mileo@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    move_line_receivable_ids = fields.Many2many(
        comodel_name='account.move.line',
        string='Receivables',
        store=True,
        compute='_compute_receivables',
    )

    eval_payment_mode_instructions = fields.Text(
        string='Instruções de Cobrança do Modo de Pagamento',
        related='payment_mode_id.instructions',
        readonly=True,
    )

    instructions = fields.Text(
        string='Instruções de cobrança',
    )

    # eval_situacao_pagamento = fields.Selection(
    #     string=u'Situação do Pagamento',
    #     related='move_line_receivable_id.situacao_pagamento',
    #     readonly=True,
    #     store=True,
    #     index=True,
    # )

    @api.multi
    @api.depends('state', 'move_id.line_ids', 'move_id.line_ids.account_id')
    def _compute_receivables(self):
        for record in self:
            lines = self.env['account.move.line']
            for line in record.move_id.line_ids:
                if (line.account_id.id == record.account_id.id
                        and line.account_id.internal_type in ('receivable',
                                                              'payable')):
                    lines |= line
            record.move_line_receivable_ids = lines.sorted()

    @api.onchange('payment_mode_id')
    def _onchange_payment_mode_id(self):
        tax_analytic_tag_id = self.env.ref(
            'l10n_br_account_payment_order.account_analytic_tag_tax')

        to_remove_invoice_line_ids = self.invoice_line_ids.filtered(
            lambda i: tax_analytic_tag_id in i.analytic_tag_ids
        )

        self.invoice_line_ids -= to_remove_invoice_line_ids

        payment_mode_id = self.payment_mode_id
        if payment_mode_id.product_tax_id:
            invoice_line_data = {
                'name': 'Taxa adicional do modo de pagamento escolhido',
                'partner_id': self.partner_id.id,
                'account_id': payment_mode_id.product_tax_account_id.id,
                'product_id': payment_mode_id.product_tax_id.id,
                'price_unit': payment_mode_id.product_tax_id.lst_price,
                'quantity': 1,
                'analytic_tag_ids': [(6, 0, [tax_analytic_tag_id.id])],
            }

            self.update(
                {
                    'invoice_line_ids': [
                        (6, 0, self.invoice_line_ids.ids),
                        (0, 0, invoice_line_data),
                    ]
                }
            )

    # TODO: Criar um movimento de baixa
    def _remove_payment_order_line(self, _raise=True):
        """ Try to search payment orders related to the account move of this
        invoice, we can't remove a payment.order.line / bank.line of a invoice
        that already sent to the bank.

        The only way to do that is to say that you want to cancel it.

        Creating a new move of "BAIXA/ESTORNO"

        :param _raise:
        :return:
        """
        move_line_receivable_ids = self.move_line_receivable_ids
        payment_order_ids = self.env['account.payment.order']

        payment_order_ids |= self.env['account.payment.order'].search([
            ('payment_line_ids.move_line_id', 'in', move_line_receivable_ids.ids),
        ])

        if payment_order_ids:
            draft_cancel_payment_order_ids = payment_order_ids.filtered(
                lambda p: p.state in ('draft', 'cancel')
            )
            if payment_order_ids - draft_cancel_payment_order_ids:
                if _raise:
                    raise UserError(_(
                        'A fatura não pode ser cancelada pois a mesma já se '
                        'encontra exportada por uma ordem de pagamento. \n',
                        'Envie um novo lançamento solicitando a Baixa/Cancelamento'
                    ))

            for po_id in draft_cancel_payment_order_ids:
                p_line_id = self.env['account.payment.line']
                for line in move_line_receivable_ids:
                    p_line_id |= self.env['account.payment.line'].search([
                        ('order_id', '=', po_id.id),
                        ('move_line_id', '=', line.id)])
                po_id.payment_line_ids -= p_line_id

    @api.multi
    def action_invoice_cancel(self):
        """ Before cancel the invoice, check if this invoice have any payment order
        related to it.
        :return:
        """
        for record in self:
            record._remove_payment_order_line()
        return super().action_invoice_cancel()

    @api.multi
    def get_invoice_fiscal_number(self):
        """ Como neste modulo nao temos o numero do documento fiscal,
        vamos retornar o numero do core e deixar este metodo
        para caso alguem queira sobrescrever"""
        self.ensure_one()
        return self.number

    @api.multi
    def _pos_action_move_create(self):
        for inv in self:
            # TODO - apesar do campo move_line_receivable_ids ser do tipo
            #  compute esta sendo preciso chamar o metodo porque as vezes
            #  ocorre da linha vir vazia o que impede de entrar no FOR
            #  abaixo causando o não preenchimento de dados usados no Boleto,
            #  isso deve ser melhor investigado
            if not inv.payment_mode_id:
                continue
            inv._compute_receivables()

            # Verifica se gera Ordem de Pagamento
            if not inv.payment_mode_id.payment_order_ok:
                continue

            for index, interval in enumerate(inv.move_line_receivable_ids):
                inv_number = inv.get_invoice_fiscal_number().split('/')[-1].zfill(8)
                numero_documento = inv_number + '/' + str(index + 1).zfill(2)

                sequence = inv.payment_mode_id.get_own_number_sequence(
                    inv, numero_documento)

                interval.transaction_ref = sequence
                interval.own_number = (
                    sequence if interval.payment_mode_id.generate_own_number
                    else '0'
                )
                interval.document_number = numero_documento
                interval.company_title_identification = hex(interval.id).upper()
                instructions = ''
                if inv.eval_payment_mode_instructions:
                    instructions = inv.eval_payment_mode_instructions + '\n'
                if inv.instructions:
                    instructions += inv.instructions + '\n'
                interval.instructions = instructions
                # Codigo de Instrução da Remessa - '01 - Remessa*'
                interval.movement_instruction_code = '01'

    @api.multi
    def action_move_create(self):
        result = super().action_move_create()
        self._pos_action_move_create()
        return result

    @api.multi
    def create_account_payment_line_baixa(self, amount_payment):
        """
        Em caso de CNAB é preciso verificar e criar linha(s)
         com Codigo de Instrução do Movimento para Remessa
         - 02 - Pedido de Baixa
        :param amount_payment:
        :return:
        """

        for inv in self:
            if not inv.payment_mode_id.payment_order_ok:
                # TODO - deveria fazer algo, testar
                return False

            applicable_lines = inv.move_id.line_ids.filtered(
                lambda x: (
                    x.payment_mode_id.payment_order_ok
                    and x.account_id.internal_type in ('receivable', 'payable')
                ))

            if not applicable_lines:
                raise UserError(_(
                    'No Payment Line created for invoice %s because '
                    "it's internal type isn't receivable or payable."
                ) % inv.number)

            payment_modes = applicable_lines.mapped('payment_mode_id')

            if not payment_modes:
                raise UserError(_('No Payment Mode on invoice %s') % inv.number)

            result_payorder_ids = []
            apoo = self.env['account.payment.order']
            for payment_mode in payment_modes:
                payorder = apoo.search([
                    ('payment_mode_id', '=', payment_mode.id),
                    ('state', '=', 'draft')], limit=1)

                new_payorder = False
                if not payorder:
                    payorder = apoo.create(
                        inv._prepare_new_payment_order(payment_mode)
                    )
                    new_payorder = True
                result_payorder_ids.append(payorder.id)
                count = 0
                line_to_update_cnab = self.env['account.move.line']
                for line in applicable_lines.filtered(
                    lambda x: x.payment_mode_id == payment_mode
                ):
                    # Identificar a Linha CNAB que vai ser dado Baixa,
                    # é preciso que o valor que está sendo pago seja igual
                    # ao valor de uma das Parcelas em aberto ou ao Valor
                    # Total pois até onde vi não há possibilidade de
                    # uma baixa parcial para ser enviada na Remessa CNAB
                    if line.debit == amount_payment:
                        line_to_update_cnab |= line

                if not line_to_update_cnab:
                    # Baixar todas as Parcelas em aberto
                    if inv.amount_total == amount_payment:
                        line_to_update_cnab |= applicable_lines
                    else:
                        # TODO - existe possibilidade de baixas parciais ?
                        raise UserError(_(
                            'O valor de Pagamento R$ %d da fatura %s não pode'
                            ' ser realizado porque é preciso que o valor seja '
                            'igual a uma das Parcelas ou ao Valor Total da'
                            ' Fatura para ser possível ser feito o Pedido de Baixa'
                            ' do Título junto ao Banco via CNAB, não é possível.'
                        ) % (amount_payment, inv.number))

                line_update = False
                for line in line_to_update_cnab:
                    # TODO - O Banco aceita receber uma instrução parcial ou
                    #  isso precisa ser resolvido de outra forma ?
                    # Existe o caso do cliente pagar antecipadamente um valor
                    # como um "Sinal" ( em vendas de produtos de alto valor
                    # para garantir a intenção é pedido um pagto como uma
                    # garantia de intenção e assim evitar prejuízos por
                    # desistencia ) caso a Ordem de Pagto ainda não tenha sido
                    # enviada ao Banco apagamos a Linha
                    if line.cnab_state in ('draft', 'added'):
                        line.payment_line_ids.unlink()
                        line.message_post(body=_(
                            'Removida Linha de Pagamento que seria enviada'
                            ' ao Banco %s via CNAB porque foi feito o pagamento'
                            ' de %d antes do envio.') % (
                            inv.payment_mode_id.fixed_journal_id.bank_id.name,
                            amount_payment))
                    # Atualização do Codigo de Instrução do Movimento
                    # para Remessa - 02 - Pedido de Baixa
                    if line.cnab_state in ('exported', 'accepted'):
                        line_update = True
                        line.movement_instruction_code = '02'
                        line.payment_situation = 'paga'
                        line.message_post(body=_(
                            'Atualizado o Codigo de Instrução do Movimento'
                            ' para Pedido de Baixa do Título, motivo pagamento'
                            'realizado por outra forma.'))
                        line.create_payment_line_from_move_line(payorder)
                        count += 1

                if line_update:
                    if new_payorder:
                        inv.message_post(body=_(
                            '%d payment lines added to the new draft payment '
                            'order %s which has been automatically created.'
                        ) % (count, payorder.name))
                    else:
                        inv.message_post(body=_(
                            '%d payment lines added to the existing draft '
                            'payment order %s.'
                        ) % (count, payorder.name))

    @api.multi
    def invoice_validate(self):
        result = super().invoice_validate()
        filtered_invoice_ids = self.filtered(lambda s: s.payment_mode_id)
        if filtered_invoice_ids:
            for filtered_invoice_id in filtered_invoice_ids:
                # TODO - essa validação já é feita no super, confirmar
                #  com o teste do modo de pagto q não deve gerar Ordem
                #  de Pagto, modo Cheque
                if filtered_invoice_id.payment_mode_id.payment_order_ok:
                    filtered_invoice_id.create_account_payment_line()
        return result

    @api.multi
    def assign_outstanding_credit(self, credit_aml_id):
        self.ensure_one()

        # TODO - Existe necessidade de ser feito algo nesse metodo ?
        #  Criar o teste do caso de uso de um Pagto por fora do CNAB
        #  p/ validar
        # if self.eval_situacao_pagamento in ['paga', 'liquidada',
        # 'baixa_liquidacao']:
        #    raise UserError(
        #       _(
        #         'Não é possível adicionar pagamentos em uma fatura que '
        #         'já está paga.'
        #         )
        #        )
        # if self.eval_state_cnab in ['accepted', 'exported', 'done']:
        #    raise UserError(
        #      _(
        #        'Não é possível adicionar pagamentos em uma fatura já '
        #        'exportada ou aceita no banco.'
        #        )
        #     )
        return super().assign_outstanding_credit(credit_aml_id)

    @api.multi
    def register_payment(
        self, payment_line, writeoff_acc_id=False, writeoff_journal_id=False
    ):
        res = super().register_payment(
            payment_line, writeoff_acc_id, writeoff_journal_id)

        self._pos_action_move_create()

        for inv in self:
            inv._compute_receivables()
            receivable_id = inv.move_line_receivable_ids
            receivable_id.residual = inv.residual

        return res
