# -*- coding: utf-8 -*-
# © 2013-2016 Yannick Vaucher (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{'name': 'PostLogistics Labels WebService',
 'version': '10.0.1.2.1',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'summary': 'Print postlogistics shipping labels',
 'license': 'AGPL-3',
 'category': 'Delivery',
 'complexity': 'normal',
 'depends': ['base_delivery_carrier_label',
             'configuration_helper',
             'web_domain_field'],
 'website': 'https://github.com/OCA/delivery-carrier',
 'data': ['data/partner.xml',
          'data/product.xml',
          'data/delivery.xml',
          'views/delivery.xml',
          'views/postlogistics_license.xml',
          'views/res_config.xml',
          'views/stock.xml',
          'security/ir.model.access.csv',
          ],
 'installable': True,
 'auto_install': False,
 'application': True,
 'external_dependencies': {
     'python': ['suds'],
 },
 'post_load': 'patch_suds',
 }
