# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectTask(models.Model):
    _name = "project.task"
    _inherit = [
        "project.task",
    ]

    direct_feature_implementation_ids = fields.Many2many(
        string="Direct Feature Implementation",
        comodel_name="odoo_feature_implementation",
        relation="rel_feature_implementation_2_direct_task",
        column1="task_id",
        column2="feature_implementation_id",
    )
