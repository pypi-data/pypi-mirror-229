# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OdooDeployment(models.Model):
    _name = "odoo_deployment"
    _inherit = [
        "odoo_deployment",
    ]

    task_id = fields.Many2one(
        string="Task",
        comodel_name="project.task",
    )
    project_id = fields.Many2one(
        string="Project",
        related="task_id.project_id",
        store=False,
    )
    task_stage_id = fields.Many2one(
        string="Task Stage",
        related="task_id.stage_id",
        store=True,
        readonly=False,
    )
    task_state = fields.Selection(
        string="Task State",
        related="task_id.state",
        store=True,
        readonly=False,
    )
    auto_create_task = fields.Boolean(
        string="Auto Create Task",
        default=False,
    )
    create_task_ok = fields.Boolean(
        string="Can Create Task",
        compute="_compute_task_ok",
        store=False,
        compute_sudo=True,
    )
    delete_task_ok = fields.Boolean(
        string="Can Delete Task",
        compute="_compute_task_ok",
        store=False,
        compute_sudo=True,
    )

    @api.depends(
        "state",
        "task_id",
    )
    def _compute_task_ok(self):
        for record in self:
            create_task_ok = delete_task_ok = True

            if record.state != "open":
                create_task_ok = delete_task_ok = False

            if record.task_id:
                create_task_ok = False

            if not record.task_id:
                delete_task_ok = False

            record.create_task_ok = create_task_ok
            record.delete_task_ok = delete_task_ok

    def action_create_task(self):
        for record in self.sudo():
            record._create_task()

    def action_delete_task(self):
        for record in self.sudo():
            record._delete_task()

    def _delete_task(self):
        self.ensure_one()
        task = self.task_id

        if not task:
            return True

        self.write({"task_id": False})
        task.unlink()

    def _create_task(self):
        self.ensure_one()
        task = self.env["project.task"].create(self._prepare_task())
        self.write(
            {
                "task_id": task.id,
            }
        )

    def _prepare_task(self):
        self.ensure_one()
        return {
            "name": self.name,
            "user_id": self.user_id.id,
            "project_id": self.implementation_id.project_id.id,
            "type_id": self.implementation_id.task_type_id.id,
            "timebox_ids": self._get_task_timebox(),
            "stage_id": self.implementation_id.task_stage_id
            and self.implementation_id.task_stage_id.id
            or False,
            "work_estimation": self.implementation_id.task_type_id.work_estimation,
        }

    def _get_task_timebox(self):
        self.ensure_one()
        Timebox = self.env["task.timebox"]
        criteria = [
            ("date_start", "<=", self.date),
            ("date_end", ">=", self.date),
            ("state", "!=", "done"),
        ]
        timeboxes = Timebox.search(criteria)

        if len(timeboxes) == 0:
            error_message = _(
                """
            Context: Create task from odoo deployment
            Database ID: %s
            Problem: No timebox
            Solution: Create timebox
            """
                % (self.id)
            )
            raise ValidationError(error_message)

        return [(6, 0, timeboxes.ids)]
