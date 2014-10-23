# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2009  Renato Lima - Akretion                                  #
#                                                                             #
#This program is free software: you can redistribute it and/or modify         #
#it under the terms of the GNU Affero General Public License as published by  #
#the Free Software Foundation, either version 3 of the License, or            #
#(at your option) any later version.                                          #
#                                                                             #
#This program is distributed in the hope that it will be useful,              #
#but WITHOUT ANY WARRANTY; without even the implied warranty of               #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
#GNU Affero General Public License for more details.                          #
#                                                                             #
#You should have received a copy of the GNU Affero General Public License     #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.        #
###############################################################################

import time

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp
from .res_company import COMPANY_FISCAL_TYPE, COMPANY_FISCAL_TYPE_DEFAULT


class AccountFiscalPositionRuleTemplate(models.Model):
    _inherit = 'account.fiscal.position.rule.template'

    partner_fiscal_type_id = fields.Many2one(
        'l10n_br_account.partner.fiscal.type', 'Tipo Fiscal do Parceiro')
    fiscal_category_id = fields.Many2one(
        'l10n_br_account.fiscal.category', 'Categoria')
    fiscal_type = fields.Selection(
        COMPANY_FISCAL_TYPE, u'Regime Tributário', required=True,
        default=COMPANY_FISCAL_TYPE_DEFAULT)
    revenue_start = fields.Float(
        'Faturamento Inicial', digits_compute=dp.get_precision('Account'),
        default=0.00, help="Faixa inicial de faturamento bruto")
    revenue_end = fields.Float(
        'Faturamento Final', digits_compute=dp.get_precision('Account'),
        default=0.00, help="Faixa inicial de faturamento bruto")
    parent_id = fields.Many2one(
        'account.fiscal.position.rule.template', 'Regra Pai')
    child_ids = fields.One2many(
        'account.fiscal.position.rule.template', 'parent_id', 'Regras Filhas')


class AccountFiscalPositionRule(models.Model):
    _inherit = 'account.fiscal.position.rule'

    partner_fiscal_type_id = fields.Many2one(
        'l10n_br_account.partner.fiscal.type', 'Tipo Fiscal do Parceiro')
    fiscal_category_id = fields.Many2one(
        'l10n_br_account.fiscal.category', 'Categoria')
    fiscal_type = fields.Selection(
        COMPANY_FISCAL_TYPE, u'Regime Tributário', required=True,
        default=COMPANY_FISCAL_TYPE_DEFAULT)
    revenue_start = fields.Float(
        'Faturamento Inicial', digits_compute=dp.get_precision('Account'),
        default=0.00, help="Faixa inicial de faturamento bruto")
    revenue_end = fields.Float(
        'Faturamento Final', digits_compute=dp.get_precision('Account'),
        default=0.00, help="Faixa inicial de faturamento bruto")
    parent_id = fields.Many2one('account.fiscal.position.rule', 'Regra Pai')
    child_ids = fields.One2many(
        'account.fiscal.position.rule', 'parent_id', 'Regras Filhas')

    def _map_domain(self, partner, addrs, company, **kwargs):
        from_country = company.partner_id.country_id.id
        from_state = company.partner_id.state_id.id
        fiscal_rule_parent_id = company.fiscal_rule_parent_id.id
        partner_fiscal_type_id = partner.partner_fiscal_type_id.id

        document_date = self.env.context.get('date', time.strftime('%Y-%m-%d'))
        use_domain = self.env.context.get('use_domain', ('use_sale', '=', True))

        domain = [
            '&', ('company_id', '=', company.id), use_domain,
            ('fiscal_type', '=', company.fiscal_type),
            ('fiscal_category_id', '=', kwargs.get('fiscal_category_id')),
            '|', ('partner_fiscal_type_id', '=', partner_fiscal_type_id),
            ('partner_fiscal_type_id', '=', False),
            '|', ('from_country', '=', from_country),
            ('from_country', '=', False),
            '|', ('from_state', '=', from_state),
            ('from_state', '=', False),
            '|', ('parent_id', '=', fiscal_rule_parent_id),
            ('parent_id', '=', False),
            '|', ('date_start', '=', False),
            ('date_start', '<=', document_date),
            '|', ('date_end', '=', False),
            ('date_end', '>=', document_date),
            '|', ('revenue_start', '=', False),
            ('revenue_start', '<=', company.annual_revenue),
            '|', ('revenue_end', '=', False),
            ('revenue_end', '>=', company.annual_revenue)]

        for address_type, address in addrs.items():
            key_country = 'to_%s_country' % address_type
            key_state = 'to_%s_state' % address_type
            to_country = address.country_id.id or False
            domain += [
                '|', (key_country, '=', to_country),
                (key_country, '=', False)]
            to_state = address.state_id.id or False
            domain += [
                '|', (key_state, '=', to_state), (key_state, '=', False)]

        return domain

    def product_fiscal_category_map(self, product_id, fiscal_category_id,
                                    to_state_id=None):
        result = None

        if not product_id or not fiscal_category_id:
            return result
        product_tmpl_id = self.env['product.product'].browse(product_id).id
        default_product_fiscal_category = self.env[
            'l10n_br_account.product.category'].search(
                [('product_tmpl_id', '=', product_tmpl_id),
                    ('fiscal_category_source_id', '=', fiscal_category_id),
                    '|', ('to_state_id', '=', False),
                    ('to_state_id', '=', to_state_id)])
        if default_product_fiscal_category:
            result = default_product_fiscal_category[0].id
        return result


class WizardAccountFiscalPositionRule(orm.TransientModel):
    _inherit = 'wizard.account.fiscal.position.rule'

    def action_create(self, cr, uid, ids, context=None):
        super(WizardAccountFiscalPositionRule, self).action_create(
            cr, uid, ids, context)

        obj_wizard = self.browse(cr, uid, ids[0])

        obj_fp = self.pool.get('account.fiscal.position')
        obj_fpr = self.pool.get('account.fiscal.position.rule')
        obj_fpr_templ = self.pool.get('account.fiscal.position.rule.template')

        company_id = obj_wizard.company_id.id
        pfr_ids = obj_fpr_templ.search(cr, uid, [])

        for fpr_template in obj_fpr_templ.browse(cr, uid, pfr_ids):

            from_country = fpr_template.from_country.id or False
            from_state = fpr_template.from_state.id or False
            to_invoice_country = fpr_template.to_invoice_country.id or False
            to_invoice_state = fpr_template.to_invoice_state.id or False
            partner_ft_id = fpr_template.partner_fiscal_type_id.id or False
            fiscal_category_id = fpr_template.fiscal_category_id.id or False

            fiscal_position_id = False
            fp_id = obj_fp.search(
                cr, uid, [('name', '=', fpr_template.fiscal_position_id.name),
                ('company_id', '=', company_id)],)

            if fp_id:
                fiscal_position_id = fp_id[0]

            fprt_id = obj_fpr.search(
                cr, uid,
                [('name', '=', fpr_template.name),
                ('company_id', '=', company_id),
                ('description', '=', fpr_template.description),
                ('from_country', '=', from_country),
                ('from_state', '=', from_state),
                ('to_invoice_country', '=', to_invoice_country),
                ('to_invoice_state', '=', to_invoice_state),
                ('use_sale', '=', fpr_template.use_sale),
                ('use_invoice', '=', fpr_template.use_invoice),
                ('use_purchase', '=', fpr_template.use_purchase),
                ('use_picking', '=', fpr_template.use_picking),
                ('fiscal_position_id', '=', fiscal_position_id)])

            if fprt_id:
                obj_fpr.write(
                    cr, uid, fprt_id, {
                        'partner_fiscal_type_id': partner_ft_id,
                        'fiscal_category_id': fiscal_category_id,
                        'fiscal_type': fpr_template.fiscal_type,
                        'revenue_start': fpr_template.revenue_start,
                        'revenue_end': fpr_template.revenue_end})
        return {}
