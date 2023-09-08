# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Odoo Implementation - Project Integration",
    "version": "14.0.1.5.0",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "depends": [
        "ssi_odoo_implementation",
        "ssi_project",
        "project_stage_state",
    ],
    "data": [
        "views/odoo_feature_views.xml",
        "views/odoo_implementation_views.xml",
        "views/odoo_feature_implementation_views.xml",
        "views/odoo_deployment_views.xml",
    ],
    "demo": [],
}
