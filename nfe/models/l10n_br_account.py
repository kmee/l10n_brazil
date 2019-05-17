# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2013  Danimar Ribeiro 26/06/2013
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

import os
import base64
import commands
import datetime
import logging
from odoo import models, fields, api
from odoo.exceptions import RedirectWarning
from odoo.tools.translate import _
from odoo.addons.nfe.sped.nfe.validator.config_check import \
    validate_nfe_configuration, validate_nfe_invalidate_number
from odoo.addons.nfe.sped.nfe.processing.xml import invalidate, \
    monta_caminho_nfe, monta_caminho_inutilizacao

_logger = logging.getLogger(__name__)


class L10nBrAccountInvoiceInvalidNumber(models.Model):
    _inherit = 'l10n_br_account.invoice.invalid.number'

    state = fields.Selection([('draft', 'Rascunho'),
                              ('not_authorized', 'Não autorizado'),
                              ('done', u'Autorizado Sefaz')],
                             'Status', required=True)
    status = fields.Char('Status', size=10, readonly=True)
    message = fields.Char('Mensagem', size=200, readonly=True)
    invalid_number_document_event_ids = fields.One2many(
        'l10n_br_account.document_event',
        'document_event_ids', u'Eventos',
        states={'done': [('readonly', True)]}
    )

    @api.multi
    def attach_file_event(self, seq, att_type, ext):
        """
        Implemente esse metodo na sua classe de manipulação de arquivos
        :param cr:
        :param uid:
        :param ids:
        :param seq:
        :param att_type:
        :param ext:
        :param context:
        :return:
        """
        if seq is None:
            seq = 1
        # monta_caminho_inutilizacao
        for obj in self:
            company = obj.company_id
            number_start = obj.number_start
            number_end = obj.number_end
            number_serie = self.document_serie_id.code

            if att_type == 'inu':
                save_dir = monta_caminho_inutilizacao(
                    company,
                    None,
                    number_serie,
                    number_start,
                    number_end)
                comando = 'ls ' + save_dir + \
                    '*-inu.xml| grep -E "[0-9]{41}-inu.xml"'
                if os.system(comando) == 0:
                    arquivo = commands.getoutput(comando)
                key = arquivo[-49:-8]
                str_aux = arquivo[-49:]

            try:
                file_attc = open(arquivo, 'r')
                attc = file_attc.read()

                self.env['ir.attachment'].create({
                    'name': str_aux.format(key),
                    'datas': base64.b64encode(attc),
                    'datas_fname': str_aux.format(key),
                    'description': '' or _('No Description'),
                    'res_model': 'l10n_br_account.invoice.invalid.number',
                    'res_id': obj.id
                })
            except IOError:
                key = 'erro'
            else:
                file_attc.close()

        return True

    @api.multi
    def action_draft_done(self):
        try:
            processo = self.send_request_to_sefaz()
            values = {
                'message': processo.resposta.infInut.xMotivo.valor,
            }

            if processo.resposta.infInut.cStat.valor == '102':
                values['state'] = 'done'
                values['status'] = '102'
                self.write(values)
                # context['caminho'] = processo.arquivos[0]['arquivo']
                self.attach_file_event(None, 'inu', 'xml')
            else:
                values['state'] = 'not_authorized'
                values['status'] = processo.resposta.infInut.cStat.valor
                self.write(values)

        except Exception as e:
            raise RedirectWarning(_(u'Erro!'), e.message)
        return True

    @api.multi
    def send_request_to_sefaz(self):
        for item in self:

            event_obj = self.env['l10n_br_account.document_event']

            validate_nfe_configuration(item.company_id)
            validate_nfe_invalidate_number(item.company_id, item)

            results = []
            try:
                processo = invalidate(item.company_id, item)
                vals = {
                    'type': str(processo.webservice),
                    'status': processo.resposta.infInut.cStat.valor,
                    'response': '',
                    'company_id': item.company_id.id,
                    'origin': '[INU] {0} - {1}'.format(str(item.number_start),
                                                       str(item.number_end)),
                    #    'file_sent': processo.arquivos[0]['arquivo'],
                    #    'file_returned': processo.arquivos[1]['arquivo'],
                    'message': processo.resposta.infInut.xMotivo.valor,
                    'state': 'done',
                    # 'document_event_ids': item.id} TODO: Fix me!
                }
                results.append(vals)

            except Exception as e:
                _logger.error(e.message, exc_info=True)
                vals = {
                    'type': '-1',
                    'status': '000',
                    'response': 'response',
                    'company_id': item.company_id.id,
                    'origin': '[INU] {0} - {1}'.format(str(item.number_start),
                                                       str(item.number_end)),
                    'file_sent': 'False',
                    'file_returned': 'False',
                    'message': 'Erro desconhecido ' + e.message,
                    'state': 'done',
                    # 'document_event_ids': item.id TODO: Fix me!
                }
                results.append(vals)
            finally:
                for result in results:
                    event_obj.create(result)
            return processo


class L10nBrDocumentEvent(models.Model):
    _inherit = 'l10n_br_account.document_event'

    @api.multi
    def set_done(self):
        if self is None:
            values = {'state': 'done', 'end_date': datetime.datetime.now()}
        self.write(values)
        return True
