# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _name = "helpdesk_ticket"
    _inherit = [
        "helpdesk_ticket",
    ]

    appointment_schedule_ids = fields.Many2many(
        string="Appointment Requests",
        comodel_name="appointment_request",
        relation="rel_helpdesk_ticket_2_appointment_request",
        column1="ticket_id",
        column2="request_id",
    )
    appointment_request_state = fields.Selection(
        string="Appointment Request Status",
        selection=[
            ("no_need", "Not Needed"),
            ("open", "In Progress"),
            ("done", "Done"),
        ],
        compute="_compute_appointment_request_state",
        store=True,
    )

    @api.depends(
        "appointment_schedule_ids",
        "appointment_schedule_ids.appointment_id.state",
    )
    def _compute_appointment_request_state(self):
        for record in self:
            result = "no_need"

            count_req = len(record.appointment_schedule_ids)

            if count_req > 0:
                result = "done"
                for req in record.appointment_schedule_ids:
                    if not req.appointment_id:
                        result = "open"
                    elif req.appointment_id.state != "done":
                        result = "open"

            record.appointment_request_state = result
