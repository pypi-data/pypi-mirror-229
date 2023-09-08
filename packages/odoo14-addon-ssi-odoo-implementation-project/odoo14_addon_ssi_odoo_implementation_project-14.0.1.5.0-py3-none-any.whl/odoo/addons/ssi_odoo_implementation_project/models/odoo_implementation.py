# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OdooImplementation(models.Model):
    _name = "odoo_implementation"
    _inherit = [
        "odoo_implementation",
    ]

    project_id = fields.Many2one(
        string="Project",
        comodel_name="project.project",
    )
    task_type_id = fields.Many2one(
        string="Task Type",
        comodel_name="task.type",
    )
    task_stage_id = fields.Many2one(
        string="Task Stage",
        comodel_name="project.task.type",
    )

    @api.onchange(
        "partner_id",
    )
    def onchange_project_id(self):
        self.project_id = False
