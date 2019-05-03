# Copyright (C) 2015  Luis Felipe Miléo - KMEE
# Copyright (C) 2019  Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import requests
from collections import namedtuple

from odoo import _
from odoo.exceptions import UserError


WS_SERVICOS = 0
WS_PRODUTOS = 1

WS_IBPT = {
    WS_SERVICOS: 'http://iws.ibpt.org.br/api/deolhonoimposto/Servicos/?',
    WS_PRODUTOS: 'http://iws.ibpt.org.br/api/deolhonoimposto/Produtos/?',
}


DeOlhoNoImposto = namedtuple('Config', 'token cnpj uf')


def _response_to_dict(response):
    json_acceptable_string = response.replace("'", "\"").lower()
    return json.loads(json_acceptable_string)


def _request(ws_url, params):


    try:
        response = requests.get(ws_url, params=params)
        if response.status_code == requests.codes.ok:
            data = response.json()
            return Produto(**{k.lower():v for k,v in data.items()})
        elif response.status_code == requests.codes.forbidden:
            raise UserError(_('IBPT Forbidden - token={!r}, '
                              'cnpj={!r}, UF={!r}'.format(
                              config.token, config.cnpj, config.estado)))
    except Exception as e:
        raise UserError(_('Error in the request: {0}'.format(e)))


def get_ibpt_product(config, ncm, ex='0', reference=None, description=None,
                     uom=None, amount=None, gtin=None):

    data = {
        'token': config.token,
        'cnpj': config.cnpj,
        'uf': config.uf,
        'codigo': ncm,
        'ex': ex,
        'codigoInterno': reference,
        'descricao': description,
        'unidadeMedida': uom,
        'valor': amount,
        'gtin': gtin}

    return _request(WS_IBPT[WS_PRODUTOS], data)


def get_ibpt_service(config, nbs, description=None, uom=None, amount=None):

    data = {
        'token': config.token,
        'cnpj': config.cnpj,
        'uf': config.uf,
        'codigo': nbs,
        'descricao': description,
        'unidadeMedida': uom,
        'valor': amount}

    return _request(WS_IBPT[WS_PRODUTOS], data)