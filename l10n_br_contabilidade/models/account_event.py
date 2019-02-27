# -*- coding: utf-8 -*-
# Copyright 2018 ABGF
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models

MODELS = [
    ('hr.salary.rule', 'Rúbricas Holerite'),
    ('account.invoice', 'Nota Fiscal'),
]


class AccountEvent(models.Model):
    _name = 'account.event'

    state = fields.Selection(
        string='State',
        selection=[
            ('open', 'Aberto'),
            ('validate', 'Validado'),
            ('done', 'Contabilizado'),
            ('reversed', 'Revertido'),
        ],
        default='open',
    )

    account_event_line_ids = fields.One2many(
        string='Event Lines',
        comodel_name='account.event.line',
        inverse_name='account_event_id',
    )

    data = fields.Date(
        string='Data',
    )

    ref = fields.Char(
        string='Ref'
    )

    name = fields.Char(
        string='Name',
        compute='compute_name',
    )

    origem = fields.Reference(
        string=u'origem',
        selection=MODELS,
    )

    account_event_reversao_id = fields.Many2one(
        string='Evento de reversão',
        comodel_name='account.event',
    )

    account_event_template_id = fields.Many2one(
        string='Roteiro Contábil',
        comodel_name='account.event.template',
    )

    account_move_ids = fields.One2many(
        string=u'Lançamentos',
        comodel_name='account.move',
        inverse_name='account_event_id',
    )

    @api.multi
    def compute_name(self):
        """
        """
        for record in self:
            if record.ref or record.origem and record.origem.name:
                record.name = '{} {}'.format(
                    record.ref or '', record.origem.name or '')

    def gerar_eventos(self, lines):
        """
        [{      # CAMPO CODE E VALOR OBRIGATORIO
            'code': 'LIQUIDO',
            'valor': 123,
                # INCREMENTAR DICIONARIO PARA COMPOR
                # HISTORICO PADRAO
            'name': 'Liquido do Holerite' }
         {      # CAMPO CODE E VALOR OBRIGATORIO
            'code': 'INSS',
            'valor': 621.03
                # INCREMENTAR DICIONARIO PARA COMPOR
                # HISTORICO PADRAO
            'name': 'Desconto de INSS'}
        ],

        :return:
        """

        for line in lines:
            line.update(account_event_id=self.id)
            self.env['account.event.line'].create(line)

    @api.multi
    def button_reverter_lancamentos(self):
        """
        Reverter Lançamentos do Evento Contábil
        """
        account_move_line_obj = self.env['account.move.line']

        for record in self:

            account_event_reversao_id = record.copy({
                'data': fields.Date.today(),
                'ref': 'Reversão do Evento: {}'.format(record.ref),
                'origem': '{},{}'.format('account.event', record.id),
            })

            record.account_event_reversao_id = account_event_reversao_id

            for account_move_id in record.account_move_ids:

                description = 'Reversão do Lançamento: {}/{} - {}'.format(
                    account_move_id.sequencia,
                    account_move_id.fiscalyear_id.name, account_move_id.resumo)

                period_id = \
                    self.env['account.period'].find(fields.Date.today())

                account_move_reversao = account_move_id.copy({
                    'name': description,
                    'narration': description,
                    'line_id': False,
                    'date': fields.Date.today(),
                    'period_id': period_id.id,
                    'sequencia': False,
                    'account_event_id': account_event_reversao_id.id,
                })

                for line_id in account_move_id.line_id:
                    account_move_line_obj.create({
                        'account_id': line_id.account_id.id,
                        'debit': line_id.credit,
                        'credit': line_id.debit,
                        'move_id': account_move_reversao.id,
                        'name': description,
                    })

            record.state = 'reversed'

    def criar_lancamentos(self, vals):
        """
        :param vals:
        :return:
        """
        account_move_ids = self.env['account.move']
        for lancamento in vals:
            account_move_ids += account_move_ids.create(lancamento)
        return account_move_ids

    def _preparar_dados(self):
        dados = {}

        dados['ref'] = self.ref
        dados['data'] = self.data

        period = self.env['account.period']
        dados['period_id'] = period.find(self.data).id
        dados['lines'] = []

        for line in self.account_event_line_ids:
            dados['lines'].append(
                {
                    'code': line.code,
                    'name': line.name,
                    'description': line.description,
                    'valor': line.valor,
                }
            )

        return dados

    @api.multi
    def gerar_contabilizacao(self):
        """
        Rotina principal:
        """
        for record in self:
            dados = record._preparar_dados()

            record.account_event_template_id.validar_dados(dados)

            account_move_ids = \
                record.account_event_template_id.preparar_dados_lancamentos(
                    dados)

            account_move_ids = record.criar_lancamentos(account_move_ids)

            record.account_move_ids = account_move_ids

            record.state = 'done'

    @api.multi
    def validar_evento(self):
        for record in self:
            record.state = 'validate'

    @api.multi
    def unlink(self):
        for record in self:
            record.account_move_ids.unlink()
            return super(AccountEvent, record).unlink()
