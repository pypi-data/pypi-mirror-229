# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<https://therp.nl>)
# © 2016 Akretion (Alexis de Lattre - alexis.delattre@akretion.com)
# Copyright 2016-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class AccountPaymentOrder(models.Model):
    _name = "account.payment.order"
    _description = "Payment Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    _check_company_auto = True

    name = fields.Char(string="Number", readonly=True, copy=False)
    payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode",
        required=True,
        ondelete="restrict",
        tracking=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        check_company=True,
    )
    payment_type = fields.Selection(
        selection=[("inbound", "Inbound"), ("outbound", "Outbound")],
        string="Payment Type",
        readonly=True,
        required=True,
    )
    payment_method_id = fields.Many2one(
        comodel_name="account.payment.method",
        related="payment_mode_id.payment_method_id",
        readonly=True,
        store=True,
    )
    company_id = fields.Many2one(
        related="payment_mode_id.company_id", store=True, readonly=True
    )
    company_currency_id = fields.Many2one(
        related="payment_mode_id.company_id.currency_id", store=True, readonly=True
    )
    bank_account_link = fields.Selection(
        related="payment_mode_id.bank_account_link", readonly=True
    )
    allowed_journal_ids = fields.Many2many(
        comodel_name="account.journal",
        compute="_compute_allowed_journal_ids",
        string="Allowed journals",
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Bank Journal",
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
        check_company=True,
    )
    # The journal_id field is only required at confirm step, to
    # allow auto-creation of payment order from invoice
    company_partner_bank_id = fields.Many2one(
        related="journal_id.bank_account_id",
        string="Company Bank Account",
        readonly=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("open", "Confirmed"),
            ("generated", "File Generated"),
            ("uploaded", "File Uploaded"),
            ("cancel", "Cancel"),
        ],
        string="Status",
        readonly=True,
        copy=False,
        default="draft",
        tracking=True,
    )
    date_prefered = fields.Selection(
        selection=[
            ("now", "Immediately"),
            ("due", "Due Date"),
            ("fixed", "Fixed Date"),
        ],
        string="Payment Execution Date Type",
        required=True,
        default="due",
        tracking=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    date_scheduled = fields.Date(
        string="Payment Execution Date",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
        help="Select a requested date of execution if you selected 'Due Date' "
        "as the Payment Execution Date Type.",
    )
    date_generated = fields.Date(string="File Generation Date", readonly=True)
    date_uploaded = fields.Date(string="File Upload Date", readonly=True)
    generated_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Generated by",
        readonly=True,
        ondelete="restrict",
        copy=False,
        check_company=True,
    )
    payment_line_ids = fields.One2many(
        comodel_name="account.payment.line",
        inverse_name="order_id",
        string="Transactions",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    payment_ids = fields.One2many(
        comodel_name="account.payment",
        inverse_name="payment_order_id",
        string="Payment Transactions",
        readonly=True,
    )
    payment_count = fields.Integer(
        compute="_compute_payment_count",
        string="Number of Payment Transactions",
    )
    total_company_currency = fields.Monetary(
        compute="_compute_total", store=True, currency_field="company_currency_id"
    )
    move_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="payment_order_id",
        string="Journal Entries",
        readonly=True,
    )
    move_count = fields.Integer(
        compute="_compute_move_count", string="Number of Journal Entries"
    )
    description = fields.Char()

    @api.depends("payment_mode_id")
    def _compute_allowed_journal_ids(self):
        for record in self:
            if record.payment_mode_id.bank_account_link == "fixed":
                record.allowed_journal_ids = record.payment_mode_id.fixed_journal_id
            elif record.payment_mode_id.bank_account_link == "variable":
                record.allowed_journal_ids = record.payment_mode_id.variable_journal_ids
            else:
                record.allowed_journal_ids = False

    def unlink(self):
        for order in self:
            if order.state == "uploaded":
                raise UserError(
                    _(
                        "You cannot delete an uploaded payment order. You can "
                        "cancel it in order to do so."
                    )
                )
        return super(AccountPaymentOrder, self).unlink()

    @api.constrains("payment_type", "payment_mode_id")
    def payment_order_constraints(self):
        for order in self:
            if (
                order.payment_mode_id.payment_type
                and order.payment_mode_id.payment_type != order.payment_type
            ):
                raise ValidationError(
                    _(
                        "The payment type (%s) is not the same as the payment "
                        "type of the payment mode (%s)"
                    )
                    % (order.payment_type, order.payment_mode_id.payment_type)
                )

    @api.constrains("date_scheduled")
    def check_date_scheduled(self):
        today = fields.Date.context_today(self)
        for order in self:
            if order.date_scheduled:
                if order.date_scheduled < today:
                    raise ValidationError(
                        _(
                            "On payment order %s, the Payment Execution Date "
                            "is in the past (%s)."
                        )
                        % (order.name, order.date_scheduled)
                    )

    @api.depends("payment_line_ids", "payment_line_ids.amount_company_currency")
    def _compute_total(self):
        for rec in self:
            rec.total_company_currency = sum(
                rec.mapped("payment_line_ids.amount_company_currency") or [0.0]
            )

    @api.depends("payment_ids")
    def _compute_payment_count(self):
        for order in self:
            order.payment_count = len(order.payment_ids)

    @api.depends("move_ids")
    def _compute_move_count(self):
        rg_res = self.env["account.move"].read_group(
            [("payment_order_id", "in", self.ids)],
            ["payment_order_id"],
            ["payment_order_id"],
        )
        mapped_data = {
            x["payment_order_id"][0]: x["payment_order_id_count"] for x in rg_res
        }
        for order in self:
            order.move_count = mapped_data.get(order.id, 0)

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("account.payment.order") or "New"
            )
        if vals.get("payment_mode_id"):
            payment_mode = self.env["account.payment.mode"].browse(
                vals["payment_mode_id"]
            )
            vals["payment_type"] = payment_mode.payment_type
            if payment_mode.bank_account_link == "fixed":
                vals["journal_id"] = payment_mode.fixed_journal_id.id
            if not vals.get("date_prefered") and payment_mode.default_date_prefered:
                vals["date_prefered"] = payment_mode.default_date_prefered
        return super(AccountPaymentOrder, self).create(vals)

    @api.onchange("payment_mode_id")
    def payment_mode_id_change(self):
        if len(self.allowed_journal_ids) == 1:
            self.journal_id = self.allowed_journal_ids
        if self.payment_mode_id.default_date_prefered:
            self.date_prefered = self.payment_mode_id.default_date_prefered

    def action_uploaded_cancel(self):
        self.action_cancel()
        return True

    def cancel2draft(self):
        self.write({"state": "draft"})
        return True

    def action_cancel(self):
        # Unreconcile and cancel payments
        self.payment_ids.action_draft()
        self.payment_ids.action_cancel()
        self.write({"state": "cancel"})
        return True

    def draft2open(self):
        """
        Called when you click on the 'Confirm' button
        Set the 'date' on payment line depending on the 'date_prefered'
        setting of the payment.order
        Re-generate the account payments.
        """
        today = fields.Date.context_today(self)
        for order in self:
            if not order.journal_id:
                raise UserError(
                    _("Missing Bank Journal on payment order %s.") % order.name
                )
            if (
                order.payment_method_id.bank_account_required
                and not order.journal_id.bank_account_id
            ):
                raise UserError(
                    _("Missing bank account on bank journal '%s'.")
                    % order.journal_id.display_name
                )
            if not order.payment_line_ids:
                raise UserError(
                    _("There are no transactions on payment order %s.") % order.name
                )
            # Unreconcile, cancel and delete existing account payments
            order.payment_ids.action_draft()
            order.payment_ids.action_cancel()
            order.payment_ids.unlink()
            # Prepare account payments from the payment lines
            payline_err_text = []
            group_paylines = {}  # key = hashcode
            for payline in order.payment_line_ids:
                try:
                    payline.draft2open_payment_line_check()
                except UserError as e:
                    payline_err_text.append(e.args[0])
                # Compute requested payment date
                if order.date_prefered == "due":
                    requested_date = payline.ml_maturity_date or payline.date or today
                elif order.date_prefered == "fixed":
                    requested_date = order.date_scheduled or today
                else:
                    requested_date = today
                # No payment date in the past
                requested_date = max(today, requested_date)
                # inbound: check option no_debit_before_maturity
                if (
                    order.payment_type == "inbound"
                    and order.payment_mode_id.no_debit_before_maturity
                    and payline.ml_maturity_date
                    and requested_date < payline.ml_maturity_date
                ):
                    payline_err_text.append(
                        _(
                            "The payment mode '%s' has the option "
                            "'Disallow Debit Before Maturity Date'. The "
                            "payment line %s has a maturity date %s "
                            "which is after the computed payment date %s."
                        )
                        % (
                            order.payment_mode_id.name,
                            payline.name,
                            payline.ml_maturity_date,
                            requested_date,
                        )
                    )
                # Write requested_date on 'date' field of payment line
                # norecompute is for avoiding a chained recomputation
                # payment_line_ids.date
                # > payment_line_ids.amount_company_currency
                # > total_company_currency
                with self.env.norecompute():
                    payline.date = requested_date
                # Group options
                hashcode = (
                    payline.payment_line_hashcode()
                    if order.payment_mode_id.group_lines
                    else payline.id
                )
                if hashcode in group_paylines:
                    group_paylines[hashcode]["paylines"] += payline
                    group_paylines[hashcode]["total"] += payline.amount_currency
                else:
                    group_paylines[hashcode] = {
                        "paylines": payline,
                        "total": payline.amount_currency,
                    }
            # Raise errors that happened on the validation process
            if payline_err_text:
                raise UserError(
                    _("There's at least one validation error:\n")
                    + "\n".join(payline_err_text)
                )

            order.recompute()
            # Create account payments
            payment_vals = []
            for paydict in list(group_paylines.values()):
                # Block if a bank payment line is <= 0
                if paydict["total"] <= 0:
                    raise UserError(
                        _("The amount for Partner '%s' is negative " "or null (%.2f) !")
                        % (paydict["paylines"][0].partner_id.name, paydict["total"])
                    )
                payment_vals.append(paydict["paylines"]._prepare_account_payment_vals())
            self.env["account.payment"].create(payment_vals)
        self.write({"state": "open"})
        return True

    def generate_payment_file(self):
        """Returns (payment file as string, filename)"""
        self.ensure_one()
        if self.payment_method_id.code == "manual":
            return (False, False)
        else:
            raise UserError(
                _(
                    "No handler for this payment method. Maybe you haven't "
                    "installed the related Odoo module."
                )
            )

    def open2generated(self):
        self.ensure_one()
        payment_file_str, filename = self.generate_payment_file()
        action = {}
        if payment_file_str and filename:
            attachment = self.env["ir.attachment"].create(
                {
                    "res_model": "account.payment.order",
                    "res_id": self.id,
                    "name": filename,
                    "datas": base64.b64encode(payment_file_str),
                }
            )
            simplified_form_view = self.env.ref(
                "account_payment_order.view_attachment_simplified_form"
            )
            action = {
                "name": _("Payment File"),
                "view_mode": "form",
                "view_id": simplified_form_view.id,
                "res_model": "ir.attachment",
                "type": "ir.actions.act_window",
                "target": "current",
                "res_id": attachment.id,
            }
        self.write(
            {
                "date_generated": fields.Date.context_today(self),
                "state": "generated",
                "generated_user_id": self._uid,
            }
        )
        return action

    def generated2uploaded(self):
        """Post payments and reconcile against source journal items

        Partially reconcile payments that don't match their source journal items,
        then reconcile the rest in one go.
        """
        self.payment_ids.action_post()
        # Perform the reconciliation of payments and source journal items
        for payment in self.payment_ids:
            payment_move_line_id = payment.move_id.line_ids.filtered(
                lambda x: x.account_id == payment.destination_account_id
            )
            apr = self.env["account.partial.reconcile"]
            excl_pay_lines = self.env["account.payment.line"]
            for line in payment.payment_line_ids:
                if not line.move_line_id:
                    continue
                sign = -1 if payment.payment_order_id.payment_type == "outbound" else 1
                if (
                    float_compare(
                        line.amount_currency,
                        (line.move_line_id.amount_residual_currency * sign),
                        precision_rounding=line.move_line_id.currency_id.rounding,
                    )
                    != 0
                ):
                    if line.move_line_id.amount_residual_currency < 0:
                        debit_move_id = payment_move_line_id.id
                        credit_move_id = line.move_line_id.id
                    else:
                        debit_move_id = line.move_line_id.id
                        credit_move_id = payment_move_line_id.id
                    apr.create(
                        {
                            "debit_move_id": debit_move_id,
                            "credit_move_id": credit_move_id,
                            "amount": abs(line.amount_company_currency),
                            "debit_amount_currency": abs(line.amount_currency),
                            "credit_amount_currency": abs(line.amount_currency),
                        }
                    )
                    excl_pay_lines |= line
            pay_lines = payment.payment_line_ids - excl_pay_lines
            if pay_lines:
                (pay_lines.move_line_id + payment_move_line_id).reconcile()
        self.write(
            {"state": "uploaded", "date_uploaded": fields.Date.context_today(self)}
        )
        return True

    def action_move_journal_line(self):
        self.ensure_one()
        action = self.env.ref("account.action_move_journal_line").sudo().read()[0]
        if self.move_count == 1:
            action.update(
                {
                    "view_mode": "form,tree,kanban",
                    "views": False,
                    "view_id": False,
                    "res_id": self.move_ids[0].id,
                }
            )
        else:
            action["domain"] = [("id", "in", self.move_ids.ids)]
        ctx = self.env.context.copy()
        ctx.update({"search_default_misc_filter": 0})
        action["context"] = ctx
        return action
