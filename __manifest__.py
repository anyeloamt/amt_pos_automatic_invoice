# -*- coding: utf-8 -*-
{
    'name': 'AMT POS Automatic Invoice',
    'version': '1.2',
    'category': 'Point Of Sale',
    'summary': 'Automatically create invoices for POS orders',
    'description': """
        This module adds functionality to automatically create invoices for POS orders.
    """,
    'depends': ['point_of_sale'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
    'author': 'AMT MOVIL',
    'website': 'https://www.amtmovil.com'
}