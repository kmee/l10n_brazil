# -*- coding: utf-8 -*-
#
# Copyright 2017 KMEE
#   Wagner Pereira <wagner.pereira@kmee.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from odoo import api, fields, models, _


class AgenteCausador(models.Model):
    _name = 'esocial.tipo_dependente'
    _description = 'Tipos de Dependente'
    _order = 'codigo'
    _sql_constraints = [
        ('codigo',
         'unique(codigo)',
         'Este código já existe !'
         )
    ]

    codigo = fields.Char(
        size=2,
        string='Codigo',
        required=True,
    )
    descricao = fields.Char(
<<<<<<< HEAD
<<<<<<< HEAD
        string='Nome',
=======
        string='Descrição',
>>>>>>> 919ddf3... [ADD] tabelas 5,7 e 8 e algumas correcoes
=======
        string='Nome',
>>>>>>> e6f12d3... [ADD] tabelas 5,7 e 8 e algumas correcoes
        required=True,
    )
    name = fields.Char(
        compute='_compute_name',
        store=True,
    )

    @api.onchange('codigo')
    def _valida_codigo(self):
        for tipo in self:
            if tipo.codigo:
                if tipo.codigo.isdigit():
                    tipo.codigo = tipo.codigo.zfill(2)
                else:
                    res = {'warning': {
                        'title': _('Código Incorreto!'),
                        'message': _('Campo Código somente aceita números!'
                                     ' - Corrija antes de salvar')
                    }}
                    tipo.codigo = False
                    return res

    @api.depends('codigo', 'descricao')
    def _compute_name(self):
        for tipo in self:
            tipo.name = tipo.codigo + '-' + tipo.descricao
