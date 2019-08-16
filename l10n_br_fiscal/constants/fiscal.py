# Copyright (C) 2019  Renato Lima - Akretion <renato.lima@akretion.com.br>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


COMMENT_TYPE = [
    ('fiscal', 'Fiscal'),
    ('commercial', 'Commercial')]


DEFAULT_COMMENT_TYPE = 'commercial'


PRODUCT_FISCAL_TYPE = (
    ('00', 'Mercadoria para Revenda'),
    ('01', 'Matéria-prima'),
    ('02', 'Embalagem'),
    ('03', 'Produto em Processo'),
    ('04', 'Produto Acabado'),
    ('05', 'Subproduto'),
    ('06', 'Produto Intermediário'),
    ('07', 'Material de Uso e Consumo'),
    ('08', 'Ativo Imobilizado'),
    ('09', 'Serviços'),
    ('10', 'Outros insumos'),
    ('99', 'Outras')
)

PRODUCT_FISCAL_TYPE_SERVICE = '09'

NCM_FOR_SERVICE = '0000.00.00'
NCM_FOR_SERVICE_REF = 'fiscal.ncm_00000000'

TAX_DOMAIN = (
    ('ipi', 'IPI'),
    ('icms', 'ICMS - Próprio'),
    ('icmsfcp', 'ICMS FCP - Fundo de Combate a Pobreza'),
    ('icmsdifal', 'ICMS - Interstatual'),
    ('icmsst', 'ICMS - Subistituição Tributária'),
    ('pis', 'PIS'),
    ('pisst', 'PIS ST'),
    ('cofins', 'COFINS'),
    ('cofinsst', 'COFINS ST'),
    ('issqn', 'ISSQN'),
    ('irpj', 'IRPJ'),
    ('ir', 'IR'),
    ('csll', 'CSLL'),
    ('ii', 'II'),
    ('simples', 'Simples Nacional'),
    ('others', 'Outros')
)


TAX_FRAMEWORK = (
    ('1', '1 - Simples Nacional'),
    ('2', '2 - Simples Nacional – excesso de sublimite da receita bruta'),
    ('3', '3 - Regime Normal')
)


TAX_FRAMEWORK_DEFAULT = '3'


CERTIFICATE_TYPE = (
    ('e-cpf', 'E-CPF'),
    ('e-cnpj', 'E-CNPJ'),
    ('nf-e', 'NF-e')
)


CERTIFICATE_TYPE_DEFAULT = 'nf-e'


CERTIFICATE_SUBTYPE = (
    ('a1', 'A1'),
    ('a1', 'A3'),
)


CERTIFICATE_SUBTYPE_DEFAULT = 'a1'


FISCAL_IN_OUT = (
    ('in', 'In'),
    ('out', 'Out')
)


FISCAL_IN_OUT_ALL = (
    ('in', 'In'),
    ('out', 'Out'),
    ('all', 'All')
)


FISCAL_IN_OUT_DEFAULT = 'in'


DOCUMENT_TYPE = (
    ('icms', 'ICMS'),
    ('service', 'Serviço Municipal')
)


DOCUMENT_ISSUER = (
    ('0', 'Emissão Própria'),
    ('1', 'Terceiros')
)


CFOP_DESTINATION = (
    ('1', 'Operação Interna'),
    ('2', 'Operação Interestadual'),
    ('3', 'Operação com Exterior')
)


CEST_SEGMENT = (
    ('01', 'Autopeças'),
    ('02', 'Bebidas alcoólicas, exceto cerveja e chope'),
    ('03', 'Cervejas, chopes, refrigerantes, águas e outras bebidas'),
    ('04', 'Cigarros e outros produtos derivados do fumo'),
    ('05', 'Cimentos'),
    ('06', 'Combustíveis e lubrificantes'),
    ('07', 'Energia elétrica'),
    ('08', 'Ferramentas'),
    ('09', 'Lâmpadas, reatores e “starter”'),
    ('10', 'Materiais de construção e congêneres'),
    ('11', 'Materiais de limpeza'),
    ('12', 'Materiais elétricos'),
    ('13', 'Medicamentos de uso humano e outros produtos'
     ' farmacêuticos para uso humano ou veterinário'),
    ('14', 'Papéis, plásticos, produtos cerâmicos e vidros'),
    ('15', 'Pneumáticos, câmaras de ar e protetores de borracha'),
    ('16', 'Produtos alimentícios'),
    ('17', 'Produtos de papelaria'),
    ('18', 'Produtos de perfumaria e de higiene pessoal e cosméticos'),
    ('19', 'Produtos eletrônicos, eletroeletrônicos e eletrodomésticos'),
    ('20', 'Rações para animais domésticos'),
    ('21', 'Sorvetes e preparados para fabricação de sorvetes em máquinas'),
    ('22', 'Tintas e vernizes'),
    ('23', 'Veículos automotores'),
    ('24', 'Veículos de duas e três rodas motorizados'),
    ('25', 'Venda de mercadorias pelo sistema porta a porta'))


NFE_IND_IE_DEST = [
    ('1', '1 - Contribuinte do ICMS'),
    ('2', '2 - Contribuinte Isento do ICMS'),
    ('9', '9 - Não Contribuinte')
]

NFE_IND_IE_DEST_DEFAULT = NFE_IND_IE_DEST[0][0]

NFE_IND_IE_DEST_1 = '1'
NFE_IND_IE_DEST_2 = '2'
NFE_IND_IE_DEST_3 = '9'


CFOP_TYPE_MOVE = [
    ('purchase_industry', 'Purchase Industry'),
    ('purchase_commerce', 'Purchase Commerce'),
    ('purchase_asset', 'Purchase Asset'),
    ('purchase_ownuse', 'Purchase Own Use'),
    ('purchase_service', 'Purchase Service'),
    ('purchase_refund', 'Purchase Refund'),
    ('return_in', 'Return in'),
    ('sale_industry', 'Sale Industry'),
    ('sale_commerce', 'Sale Commerce'),
    ('sale_asset', 'Sale Asset'),
    ('sale_ownuse', 'Sale Own Use'),
    ('sale_service', 'Sale Service'),
    ('sale_refund', 'Sale Refund'),
    ('return_out', 'Return Out'),
    ('other', 'Other')]

CFOP_TYPE_MOVE_DEFAULT = 'other'
