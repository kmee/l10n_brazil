# -*- coding: utf-8 -*-
# © 2016 KMEE INFORMATICA LTDA (https://kmee.com.br)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    @api.depends('invoice_id.nfe_access_key',
                 'invoice_ids.nfe_access_key',
                 'pos_order_ids.chave_cfe')
    def _get_fiscal_document_access_key(self):
        for picking in self:
            pos_order_access_key = [order.chave_cfe
                                    for order in picking.pos_order_ids
                                    if picking.pos_order_ids] or ['']
            picking.fiscal_document_access_key = (
                (picking.invoice_id and picking.invoice_id.nfe_access_key)
                or pos_order_access_key[0] or '')

    fiscal_document_access_key = fields.Char(
        u'Chave de acesso do Documento', compute_sudo=True,
        compute=_get_fiscal_document_access_key,
        store=True)
