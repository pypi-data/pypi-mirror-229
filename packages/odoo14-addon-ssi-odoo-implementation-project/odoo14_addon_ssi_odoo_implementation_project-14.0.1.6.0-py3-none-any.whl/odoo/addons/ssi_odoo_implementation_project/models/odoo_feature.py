# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OdooFeature(models.Model):
    _name = "odoo_feature"
    _inherit = ["odoo_feature"]

    project_id = fields.Many2one(
        string="Project",
        comodel_name="project.project",
    )
    task_ids = fields.Many2many(
        string="Tasks",
        comodel_name="project.task",
        relation="rel_feature_2_task",
        column1="feature_id",
        column2="task_id",
    )
    num_task = fields.Integer(
        string="Number of Tasks",
        compute="_compute_num_task",
        store=True,
    )
    num_draft_task = fields.Integer(
        string="Number of Draft Tasks",
        compute="_compute_num_task",
        store=True,
    )
    num_open_task = fields.Integer(
        string="Number of Open Tasks",
        compute="_compute_num_task",
        store=True,
    )
    num_done_task = fields.Integer(
        string="Number of Done Tasks",
        compute="_compute_num_task",
        store=True,
    )
    num_cancel_task = fields.Integer(
        string="Number of Cancel Tasks",
        compute="_compute_num_task",
        store=True,
    )
    num_pending_task = fields.Integer(
        string="Number of Pending Tasks",
        compute="_compute_num_task",
        store=True,
    )

    @api.depends(
        "task_ids",
        "task_ids.stage_id",
    )
    def _compute_num_task(self):
        for record in self:
            total = (
                total_draft
            ) = total_open = total_done = total_pending = total_cancel = 0
            for task in record.task_ids:
                total += 1
                if task.state == "draft":
                    total_draft += 1
                elif task.state == "open":
                    total_open += 1
                elif task.state == "done":
                    total_done += 1
                elif task.state == "pending":
                    total_pending += 1
                elif task.state == "cancelled":
                    total_cancel += 1
            record.num_task = total
            record.num_draft_task = total_draft
            record.num_open_task = total_open
            record.num_done_task = total_done
            record.num_cancel_task = total_cancel
            record.num_pending_task = total_pending
