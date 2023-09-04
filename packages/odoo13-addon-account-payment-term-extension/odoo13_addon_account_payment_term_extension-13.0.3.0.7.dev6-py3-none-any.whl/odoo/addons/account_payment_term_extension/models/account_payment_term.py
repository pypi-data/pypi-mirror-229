# Copyright 2013-2016 Camptocamp SA (Yannick Vaucher)
# Copyright 2004-2016 Odoo S.A. (www.odoo.com)
# Copyright 2015-2016 Akretion
# (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2018 Simone Rubino - Agile Business Group
# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2021 Tecnativa - Pedro M. Baeza
# Copyright 2021 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import calendar
from functools import reduce

from dateutil.relativedelta import relativedelta

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_is_zero, float_round


class AccountPaymentTermHoliday(models.Model):
    _name = "account.payment.term.holiday"
    _description = "Payment Term Holidays"

    payment_id = fields.Many2one(comodel_name="account.payment.term")
    holiday = fields.Date(required=True)
    date_postponed = fields.Date(string="Postponed date", required=True)

    @api.constrains("holiday", "date_postponed")
    def check_holiday(self):
        for record in self:
            if fields.Date.from_string(
                record.date_postponed
            ) <= fields.Date.from_string(record.holiday):
                raise ValidationError(
                    _("Holiday %s can only be postponed into the future")
                    % record.holiday
                )
            if (
                record.search_count(
                    [
                        ("payment_id", "=", record.payment_id.id),
                        ("holiday", "=", record.holiday),
                    ]
                )
                > 1
            ):
                raise ValidationError(
                    _("Holiday %s is duplicated in current payment term")
                    % record.holiday
                )
            if (
                record.search_count(
                    [
                        ("payment_id", "=", record.payment_id.id),
                        "|",
                        ("date_postponed", "=", record.holiday),
                        ("holiday", "=", record.date_postponed),
                    ]
                )
                >= 1
            ):
                raise ValidationError(
                    _("Date %s cannot is both a holiday and a Postponed date")
                    % record.holiday
                )


class AccountPaymentTermLine(models.Model):
    _inherit = "account.payment.term.line"

    amount_round = fields.Float(
        string="Amount Rounding",
        digits="Account",
        # TODO : I don't understand this help msg ; what is surcharge ?
        help="Sets the amount so that it is a multiple of this value.\n"
        "To have amounts that end in 0.99, set rounding 1, "
        "surcharge -0.01",
    )
    months = fields.Integer(string="Number of Months")
    weeks = fields.Integer(string="Number of Weeks")
    value = fields.Selection(
        selection_add=[
            ("percent_amount_untaxed", "Percent (Untaxed amount)"),
            ("fixed",),
        ]
    )

    @api.constrains("value", "value_amount")
    def _check_value_amount_untaxed(self):
        for term_line in self:
            if (
                term_line.value == "percent_amount_untaxed"
                and not 0 <= term_line.value_amount <= 100
            ):
                raise ValidationError(
                    _(
                        "Percentages on the Payment Terms lines "
                        "must be between 0 and 100."
                    )
                )

    def compute_line_amount(self, total_amount, remaining_amount, precision_digits):
        """Compute the amount for a payment term line.
        In case of procent computation, use the payment
        term line rounding if defined

            :param total_amount: total balance to pay
            :param remaining_amount: total amount minus sum of previous lines
                computed amount
            :returns: computed amount for this line
        """
        self.ensure_one()
        if self.value == "fixed":
            return float_round(self.value_amount, precision_digits=precision_digits)
        elif self.value in ("percent", "percent_amount_untaxed"):
            amt = total_amount * self.value_amount / 100.0
            if self.amount_round:
                amt = float_round(amt, precision_rounding=self.amount_round)
            return float_round(amt, precision_digits=precision_digits)
        elif self.value == "balance":
            return float_round(remaining_amount, precision_digits=precision_digits)
        return None

    def _decode_payment_days(self, days_char):
        # Admit space, dash and comma as separators
        days_char = days_char.replace(" ", "-").replace(",", "-")
        days_char = [x.strip() for x in days_char.split("-") if x]
        days = [int(x) for x in days_char]
        days.sort()
        return days

    @api.constrains("payment_days")
    def _check_payment_days(self):
        for record in self:
            if not record.payment_days:
                continue
            try:
                payment_days = record._decode_payment_days(record.payment_days)
                error = any(day <= 0 or day > 31 for day in payment_days)
            except Exception:
                error = True
            if error:
                raise exceptions.Warning(_("Payment days field format is not valid."))

    payment_days = fields.Char(
        string="Payment day(s)",
        help="Put here the day or days when the partner makes the payment. "
        "Separate each possible payment day with dashes (-), commas (,) "
        "or spaces ( ).",
    )


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    sequential_lines = fields.Boolean(
        string="Sequential lines",
        default=False,
        help="Allows to apply a chronological order on lines.",
    )
    holiday_ids = fields.One2many(
        string="Holidays",
        comodel_name="account.payment.term.holiday",
        inverse_name="payment_id",
    )

    def apply_holidays(self, date):
        holiday = self.holiday_ids.search(
            [("payment_id", "=", self.id), ("holiday", "=", date)]
        )
        if holiday:
            return fields.Date.from_string(holiday.date_postponed)
        return date

    def apply_payment_days(self, line, date):
        """Calculate the new date with days of payments"""
        if line.payment_days:
            payment_days = line._decode_payment_days(line.payment_days)
            if payment_days:
                new_date = None
                payment_days.sort()
                days_in_month = calendar.monthrange(date.year, date.month)[1]
                for day in payment_days:
                    if date.day <= day:
                        if day > days_in_month:
                            day = days_in_month
                        new_date = date + relativedelta(day=day)
                        break
                if not new_date:
                    day = payment_days[0]
                    if day > days_in_month:
                        day = days_in_month
                    new_date = date + relativedelta(day=day, months=1)
                return new_date
        return date

    def compute(self, value, date_ref=False, currency=None):
        """Complete overwrite of compute method for adding extra options."""
        # FIXME: Find an inheritable way of doing this
        self.ensure_one()
        last_account_move = self.env.context.get("last_account_move", False)
        date_ref = date_ref or fields.Date.today()
        amount = value
        result = []
        if not currency:
            if self.env.context.get("currency_id"):
                currency = self.env["res.currency"].browse(
                    self.env.context["currency_id"]
                )
            else:
                currency = self.env.user.company_id.currency_id
        precision_digits = currency.decimal_places
        next_date = fields.Date.from_string(date_ref)
        for line in self.line_ids:
            if line.value == "percent_amount_untaxed" and last_account_move:
                if last_account_move.company_id.currency_id == currency:
                    amount_untaxed = -last_account_move.amount_untaxed_signed
                else:
                    raise UserError(
                        _(
                            "Percentage of amount untaxed can't be used with foreign "
                            "currencies"
                        )
                    )
                amt = line.compute_line_amount(amount_untaxed, amount, precision_digits)
            else:
                amt = line.compute_line_amount(value, amount, precision_digits)
            if not self.sequential_lines:
                # For all lines, the beginning date is `date_ref`
                next_date = fields.Date.from_string(date_ref)
                if float_is_zero(amt, precision_digits=precision_digits):
                    continue
            if line.option == "day_after_invoice_date":
                next_date += relativedelta(
                    days=line.days, weeks=line.weeks, months=line.months
                )
            elif line.option == "day_following_month":
                # Getting last day of next month
                next_date += relativedelta(day=line.days, months=1)
            elif line.option == "day_current_month":
                # Getting last day of next month
                next_date += relativedelta(day=line.days, months=0)
            # From Odoo
            elif line.option == "after_invoice_month":
                # Getting 1st of next month
                next_first_date = next_date + relativedelta(day=1, months=1)
                # Then add days
                next_date = next_first_date + relativedelta(
                    days=line.days - 1, weeks=line.weeks, months=line.months
                )
            next_date = self.apply_payment_days(line, next_date)
            next_date = self.apply_holidays(next_date)
            if not float_is_zero(amt, precision_digits=precision_digits):
                result.append((fields.Date.to_string(next_date), amt))
                amount -= amt
        amount = reduce(lambda x, y: x + y[1], result, 0.0)
        dist = round(value - amount, precision_digits)
        if dist:
            last_date = result and result[-1][0] or fields.Date.today()
            result.append((last_date, dist))
        return result
