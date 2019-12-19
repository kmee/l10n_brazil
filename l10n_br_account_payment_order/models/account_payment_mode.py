# Copyright (C) 2012-Today - KMEE (<http://kmee.com.br>).
#  @author Luis Felipe Miléo - mileo@kmee.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"

    internal_sequence_id = fields.Many2one("ir.sequence", "Sequência")
    instrucoes = fields.Text("Instruções de cobrança")
    invoice_print = fields.Boolean("Gerar relatorio na conclusão da fatura?")

    _sql_constraints = [
        (
            "internal_sequence_id_unique",
            "unique(internal_sequence_id)",
            "Sequência já usada! Crie uma sequência unica para cada modo",
        )
    ]
