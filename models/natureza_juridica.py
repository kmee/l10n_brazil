# -*- coding: utf-8 -*-
#
# Copyright 2017 KMEE
#   Wagner Pereira <wagner.pereira@kmee.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from odoo import api, fields, models, _
from pybrasil.base import modulo11
from pybrasil.inscricao import limpa_formatacao


class NaturezaJuridica(models.Model):
    _name = 'esocial.natureza_juridica'
    _description = 'Natureza Juridica'
    _order = 'name'
    _sql_constraints = [
        ('codigo',
         'unique(codigo)',
         'Este código já existe !'
         )
    ]

    codigo = fields.Char(
        size=5,
        string='Codigo',
        required=True,
    )
    nome = fields.Char(
        string='Nome',
        required=True,
    )
    name = fields.Char(
<<<<<<< HEAD
<<<<<<< HEAD
        compute='_compute_name',
=======
        compute='_calcula_name',
>>>>>>> c7e221e... [ADD] Tabelas eSocial 01, 02, 03, 13, 14, 15, 16, 17, 18 , 19, 20 , 21, 25 e 26
=======
        compute='_compute_name',
>>>>>>> 565ad17... [FIX] PEP8
        store=True,
    )

    @api.onchange('codigo')
    def _valida_codigo(self):
        for natureza in self:
            nat = limpa_formatacao(natureza.codigo)
            if not nat.isdigit():
                res = {'warning': {
                    'title': _('Código Incorreto!'),
                    'message': _('Campo Código somente aceita números!'
                                 ' - Corrija antes de salvar')
                }}
                return res

            if not valida_natureza(nat):
                res = {'warning': {
                    'title': _('Código Incorreto!'),
                    'message': _('Dígito verificador incorreto!'
                                 ' - Corrija antes de salvar')
                }}
                return res

            natureza.codigo = formata_natureza(natureza.codigo)

    @api.depends('codigo', 'nome')
<<<<<<< HEAD
<<<<<<< HEAD
    def _compute_name(self):
=======
    def _calcula_name(self):
>>>>>>> c7e221e... [ADD] Tabelas eSocial 01, 02, 03, 13, 14, 15, 16, 17, 18 , 19, 20 , 21, 25 e 26
=======
    def _compute_name(self):
>>>>>>> 565ad17... [FIX] PEP8
        for natureza in self:
            natureza.name = natureza.codigo + '-' + natureza.nome


def formata_natureza(natureza):
    if not valida_natureza(natureza):
        return natureza

    natureza = limpa_formatacao(natureza)

    return natureza[:3] + '-' + natureza[3:4]


def valida_natureza(natureza):
    natureza = limpa_formatacao(natureza)
    if len(natureza) != 4:
        return False

    if not natureza.isdigit():
        return False

    digito = natureza[-1:]

    d1 = modulo11(natureza[:3])

    return digito == d1
