# -*- coding: utf-8 -*-
# Copyright 2020 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import base64
import logging
logger = logging.getLogger(__name__)

MOD = 'account_invoice_overdue_reminder'


class OverdueReminderStart(models.TransientModel):
    _name = 'overdue.reminder.start'
    _description = 'Wizard to reminder overdue customer invoice'

    partner_ids = fields.Many2many(
        'res.partner', string='Customers',
        domain=[('customer', '=', True), ('parent_id', '=', False)])
    user_ids = fields.Many2many(
        'res.users', string='Salesman')
    payment_ids = fields.Many2many(
        'overdue.reminder.start.payment', 'wizard_id', readonly=True)
    start_days = fields.Integer(
        string='Trigger Delay',
        help="Odoo will propose to send an overdue reminder to a customer "
        "if it has at least one invoice which is overdue for more than "
        "N days (N = trigger delay).")
    min_interval_days = fields.Integer(
        string='Minimum Delay Since Last Reminder',
        help="Odoo will not propose to send a reminder to a customer "
        "that already got a reminder for some of the same overdue invoices "
        "less than N days ago (N = Minimum Delay Since Last Reminder).")
    up_to_date = fields.Boolean(
        string='I consider that payments are up-to-date')
    company_id = fields.Many2one(
        'res.company', readonly=True, required=True,
        default=lambda self: self.env['res.company']._company_default_get())
    interface = fields.Selection(
        '_interface_selection',
        string='Wizard Interface',
        default='onebyone', required=True)
    partner_policy = fields.Selection(
        '_partner_policy_selection', required=True,
        string='Contact to Remind')

    @api.model
    def _interface_selection(self):
        return self.env['res.company']._overdue_reminder_interface_selection()

    @api.model
    def _partner_policy_selection(self):
        return self.env['res.company'].\
            _overdue_reminder_partner_policy_selection()

    @api.model
    def default_get(self, fields_list):
        res = super(OverdueReminderStart, self).default_get(fields_list)
        amo = self.env['account.move']
        company = self.env.user.company_id
        journals = self.env['account.journal'].search([
            ('company_id', '=', company.id),
            ('type', 'in', ('bank', 'cash'))])
        payments = []
        for journal in journals:
            last = amo.search(
                [('journal_id', '=', journal.id)],
                order='date desc, id desc', limit=1)
            vals = {
                'journal_id': journal.id,
                'last_entry_date': last and last.date or False,
                'last_entry_create_date': last and last.create_date or False,
                'last_entry_create_uid': last and last.create_uid.id or False,
                }
            payments.append((0, 0, vals))
        res.update({
            'payment_ids': payments,
            'start_days': company.overdue_reminder_start_days,
            'min_interval_days': company.overdue_reminder_min_interval_days,
            'partner_policy': company.overdue_reminder_partner_policy,
            })
        return res

    def _prepare_base_domain(self):
        base_domain = [
            ('company_id', '=', self.company_id.id),
            ('type', '=', 'out_invoice'),
            ('state', '=', 'open'),
            ('no_overdue_reminder', '=', False),
            ]
        return base_domain

    def _prepare_remind_trigger_domain(self, base_domain):
        today = fields.Date.from_string(fields.Date.context_today(self))
        limit_date = today
        if self.start_days:
            limit_date -= relativedelta(days=self.start_days)
        limit_date_str = fields.Date.to_string(limit_date)
        domain = base_domain + [('date_due', '<', limit_date_str)]
        if self.partner_ids:
            domain.append(('commercial_partner_id', 'in', self.partner_ids.ids))
        if self.user_ids:
            domain.append(('user_id', 'in', self.user_ids.ids))
        return domain

    def run(self):
        self.ensure_one()
        if not self.up_to_date:
            raise UserError(_(
                "In order to start overdue reminders, you must make sure that "
                "customer payments are up-to-date."))
        if self.start_days < 0:
            raise UserError(_(
                "The trigger delay cannot be negative."))
        if self.min_interval_days < 1:
            raise UserError(_(
                "The minimum delay since last reminder must be strictly positive."))
        aio = self.env['account.invoice']
        ajo = self.env['account.journal']
        rpo = self.env['res.partner']
        orso = self.env['overdue.reminder.step']
        user_id = self.env.user.id
        existing_actions = orso.search([('user_id', '=', user_id)])
        existing_actions.unlink()
        payment_journals = ajo.search([
            ('company_id', '=', self.company_id.id),
            ('type', 'in', ('bank', 'cash')),
            ])
        sale_journals = ajo.search([
            ('company_id', '=', self.company_id.id),
            ('type', '=', 'sale'),
            ])
        today = fields.Date.from_string(fields.Date.context_today(self))
        min_interval_date = fields.Date.to_string(
            today - relativedelta(days=self.min_interval_days))
        # It is important to understand this: there are 2 search on invoice :
        # 1. a first search to know if a partner must be reminded or not
        # 2. a second search to get the invoices to remind for that partner
        # There are some slight differences between these 2 searches;
        # for example: search 1 compares due_date to (today + start_days)
        # whereas search 2 compares due_date to today
        base_domain = self._prepare_base_domain()
        domain = self._prepare_remind_trigger_domain(base_domain)
        rg_res = aio.read_group(
            domain,
            ['commercial_partner_id', 'residual_company_signed'],
            ['commercial_partner_id'])
        # Sort by residual amount desc
        rg_res_sorted = sorted(
            rg_res,
            key=lambda to_sort: to_sort['residual_company_signed'],
            reverse=True)
        action_ids = []
        for rg_re in rg_res_sorted:
            commercial_partner_id = rg_re['commercial_partner_id'][0]
            commercial_partner = rpo.browse(commercial_partner_id)
            vals = self._prepare_reminder_step(
                commercial_partner, base_domain, min_interval_date,
                payment_journals, sale_journals)
            if vals:
                action = orso.create(vals)
                action_ids.append(action.id)
        if not action_ids:
            raise UserError(_(
                "There are no overdue reminders."))
        if self.interface == 'onebyone':
            xid = MOD + '.overdue_reminder_step_onebyone_action'
            action = self.env.ref(xid).read()[0]
            action['res_id'] = action_ids[0]
        elif self.interface == 'mass':
            action = orso.goto_list_view()
        return action

    def _prepare_reminder_step(
            self, commercial_partner, base_domain, min_interval_date,
            payment_journals, sale_journals):
        amlo = self.env['account.move.line']
        if commercial_partner.no_overdue_reminder:
            logger.info(
                'Skipping customer %s that has no_overdue_reminder=True',
                commercial_partner.display_name)
            return False
        invs = self.env['account.invoice'].search(
            base_domain + [
                ('commercial_partner_id', '=', commercial_partner.id),
                ('date_due', '<', fields.Date.context_today(self))])
        assert invs
        # Check min interval
        if any([
                inv.overdue_reminder_last_date > min_interval_date
                for inv in invs
                if inv.overdue_reminder_last_date]):
            logger.info(
                'Skipping customer %s that has at least one invoice '
                'with last reminder after %s',
                commercial_partner.display_name,
                min_interval_date)
            return False
        max_counter = max([inv.overdue_reminder_counter for inv in invs])
        unrec_domain = [
            ('account_id', '=', commercial_partner.property_account_receivable_id.id),
            ('partner_id', '=', commercial_partner.id),
            ('full_reconcile_id', '=', False),
            ('matched_debit_ids', '=', False),
            ('matched_credit_ids', '=', False),
            ]
        unrec_payments = amlo.search(
            unrec_domain + [
                ('journal_id', 'in', payment_journals.ids),
            ])
        unrec_refunds = amlo.search(
            unrec_domain + [
                ('journal_id', 'in', sale_journals.ids),
                ('credit', '>', 0),
            ])
        warn_unrec = unrec_payments + unrec_refunds
        if self.partner_policy == 'last_reminder':
            last_reminder = self.env['overdue.reminder.action'].search([
                ('commercial_partner_id', '=', commercial_partner.id),
                ('company_id', '=', self.company_id.id),
                ], limit=1, order='date desc, id desc')
            if last_reminder:
                partner_id = last_reminder.partner_id.id
            else:
                partner_id = commercial_partner.address_get(
                    ['invoice'])['invoice']
        elif self.partner_policy == 'last_invoice':
            last_inv = self.env['account.invoice'].search([
                ('company_id', '=', self.company_id.id),
                ('type', 'in', ('out_invoice', 'out_refund')),
                ('commercial_partner_id', '=', commercial_partner.id),
                ('state', 'in', ('open', 'paid')),
                ], order='date_invoice desc', limit=1)
            partner_id = last_inv.partner_id.id
        elif self.partner_policy == 'invoice_contact':
            partner_id = commercial_partner.address_get(
                ['invoice'])['invoice']

        vals = {
            'partner_id': partner_id,
            'commercial_partner_id': commercial_partner.id,
            'user_id': self.env.user.id,
            'invoice_ids': [(6, 0, invs.ids)],
            'company_id': self.company_id.id,
            'warn_unreconciled_move_line_ids': [(6, 0, warn_unrec.ids)],
            'counter': max_counter + 1,
            'interface': self.interface,
            }
        return vals


class OverdueReminderStartPayment(models.TransientModel):
    _name = 'overdue.reminder.start.payment'
    _description = 'Status of payments'

    wizard_id = fields.Many2one(
        'overdue.reminder.start', ondelete='cascade')
    journal_id = fields.Many2one(
        'account.journal', string='Journal', readonly=True)
    last_entry_date = fields.Date(
        string='Last Entry', readonly=True)
    last_entry_create_date = fields.Datetime(
        string='Last Entry Created on', readonly=True)
    last_entry_create_uid = fields.Many2one(
        'res.users', string='Last Entry Created by', readonly=True)


class OverdueReminderStep(models.TransientModel):
    _name = 'overdue.reminder.step'
    _description = 'Overdue reminder wizard step'

    partner_id = fields.Many2one(
        'res.partner', required=True, string='Reminder Contact')
    partner_email = fields.Char(related='partner_id.email', readonly=True)
    # for phone fields, I don't put a related field because
    # of the OCA module base_phone (when installed, this module
    # re-qualified the 'phone' and 'mobile' fields of res.partner
    # as fields.Phone()
    partner_phone = fields.Char(
        compute='_compute_phone', readonly=True, string='Phone')
    partner_mobile = fields.Char(
        compute='_compute_phone', readonly=True, string='Mobile')
    commercial_partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True, required=True)
    user_id = fields.Many2one('res.users', required=True, readonly=True)
    counter = fields.Integer(string="New Remind Counter", readonly=True)
    date = fields.Date(default=fields.Date.context_today, readonly=True)
    reminder_type = fields.Selection(
        '_reminder_type_selection', default='mail',
        string='Reminder Type', required=True)
    mail_cc_partner_ids = fields.Many2many('res.partner', string='Cc')
    mail_subject = fields.Char(string='Subject')
    mail_body = fields.Html()
    result_id = fields.Many2one(
        'overdue.reminder.result', string='Call Result/Info')
    result_notes = fields.Text(string='Call Notes')
    letter_printed = fields.Boolean(readonly=True)
    invoice_ids = fields.Many2many(
        'account.invoice', string='Overdue Invoices', readonly=True)
    company_id = fields.Many2one(
        'res.company', readonly=True, required=True,
        default=lambda self: self.env['res.company']._company_default_get())
    warn_unreconciled_move_line_ids = fields.Many2many(
        'account.move.line', string='Unreconciled Payments/Refunds',
        readonly=True)
    unreconciled_move_line_normal = fields.Boolean(
        string='Check if unreconciled payments/refunds above have a good '
               'reason not to be reconciled with an open invoice')
    interface = fields.Char(readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('skipped', 'Skipped'),
        ('done', 'Done'),
        ], default='draft', readonly=True)

    @api.model
    def _reminder_type_selection(self):
        return self.env['overdue.reminder.action']._reminder_type_selection()

    @api.depends('partner_id.phone', 'partner_id.mobile')
    def _compute_phone(self):
        for step in self:
            step.partner_phone = step.partner_id and step.partner_id.phone or False
            step.partner_mobile = step.partner_id and step.partner_id.mobile or False

    @api.model
    def create(self, vals):
        action = super(OverdueReminderStep, self).create(vals)
        commercial_partner = self.env['res.partner'].browse(
            vals['commercial_partner_id'])
        xmlid = MOD + '.overdue_invoice_reminder_mail_template'
        mail_tpl = self.env.ref(xmlid)
        mail_tpl_lang = mail_tpl.with_context(lang=commercial_partner.lang or 'en_US')
        mail_subject = mail_tpl_lang.render_template(
            mail_tpl_lang.subject, self._name, action.id)
        mail_body = mail_tpl_lang.render_template(
            mail_tpl_lang.body_html, self._name, action.id)
        if mail_tpl.user_signature:
            signature = self.env.user.signature
            if signature:
                mail_body = tools.append_content_to_html(
                    mail_body, signature, plaintext=False)
        mail_body = tools.html_sanitize(mail_body)
        action.write({
            'mail_subject': mail_subject,
            'mail_body': mail_body,
            })
        return action

    @api.onchange('reminder_type')
    def reminder_type_change(self):
        if self.reminder_type and self.reminder_type != 'phone':
            self.result_id = False
            self.result_notes = False

    def next(self):
        self.ensure_one()
        left = self.search([
            ('state', '=', 'draft'),
            ('user_id', '=', self.user_id.id),
            ('company_id', '=', self.company_id.id)], limit=1)
        if left:
            action = self.env.ref(
                MOD + '.overdue_reminder_step_onebyone_action').read()[0]
            action['res_id'] = left.id
        else:
            action = self.env.ref(
                MOD + '.overdue_reminder_end_action').read()[0]
        return action

    def goto_list_view(self):
        action = self.env.ref(
            MOD + '.overdue_reminder_step_mass_action').read()[0]
        return action

    def skip(self):
        self.write({'state': 'skipped'})
        if len(self) == 1:
            if self.interface == 'onebyone':
                action = self.next()
            else:
                action = self.goto_list_view()
            return action

    def check_warnings(self):
        self.ensure_one()
        for rec in self:
            if rec.company_id != self.env.user.company_id:
                raise UserError(_(
                    "User company is different from action company. "
                    "This should never happen."))
            if (
                    rec.warn_unreconciled_move_line_ids and
                    not rec.unreconciled_move_line_normal):
                raise UserError(_(
                    "Customer '%s' has unreconciled payments/refunds. "
                    "You should reconcile these payments/refunds and start the "
                    "overdue remind process again "
                    "(or check the option to confirm that these unreconciled "
                    "payments/refunds have a good reason not to be "
                    "reconciled with an open invoice).")
                    % rec.commercial_partner_id.display_name)

    def validate(self):
        orao = self.env['overdue.reminder.action']
        self.check_warnings()
        for rec in self:
            vals = {}
            if rec.reminder_type == 'mail':
                vals = rec.validate_mail()
            elif rec.reminder_type == 'phone':
                vals = rec.validate_phone()
            elif rec.reminder_type == 'post':
                vals = rec.validate_post()
            rec._prepare_overdue_reminder_action(vals)
            orao.create(vals)
        self.write({'state': 'done'})
        if len(self) == 1:
            if self.interface == 'onebyone':
                action = self.next()
            else:
                action = self.goto_list_view()
            return action

    def validate_mail(self):
        self.ensure_one()
        iao = self.env['ir.attachment']
        if not self.partner_id.email:
            raise UserError(_(
                "E-mail missing on partner '%s'.") % self.partner_id.display_name)
        if not self.mail_subject:
            raise UserError(_('Mail subject is empty.'))
        if not self.mail_body:
            raise UserError(_('Mail body is empty.'))
        xmlid = MOD + '.overdue_invoice_reminder_mail_template'
        mvals = self.env.ref(xmlid).generate_email(self.id)
        cc_list = [p.email for p in self.mail_cc_partner_ids if p.email]
        if mvals.get('email_cc'):
            cc_list.append(mvals['email_cc'])
        mvals.update({
            'subject': self.mail_subject,
            'body_html': self.mail_body,
            'email_cc': ', '.join(cc_list),
            'model': 'res.partner',
            'res_id': self.commercial_partner_id.id,
            })
        mvals.pop('attachment_ids', None)
        mvals.pop('attachments', None)
        mail = self.env['mail.mail'].create(mvals)


        inv_report = self.env['report']._get_report_from_name(
            'account.report_invoice')
        if self.company_id.overdue_reminder_attach_invoice:
            attachment_ids = []
            for inv in self.invoice_ids:
                if inv_report.report_type in ('qweb-html', 'qweb-pdf'):
                    res = self.env['report'].get_pdf(
                        [inv.id], 'account.report_invoice'), 'pdf'
                else:
                    context = dict(self.env.context)
                    context['report_name'] = 'account.report_invoice'
                    py3o_report = self.env['py3o.report'].create({
                        'ir_actions_report_xml_id': inv_report.id
                    }).with_context(context)
                    res = py3o_report.create_report([inv.id], {})
                    if not res:
                        raise UserError(_(
                            "Report format '%s' is not supported.")
                            % inv_report.report_type)
                report_bin, report_format = res
                # WARN : update when backporting
                filename = '%s.%s' % (inv._get_report_base_filename(), report_format)
                attach = iao.create({
                    'name': filename,
                    'datas_fname': filename,
                    'datas': base64.b64encode(report_bin),
                    'res_model': 'mail.message',
                    'res_id': mail.mail_message_id.id,
                    })
                attachment_ids.append(attach.id)
            mail.write({'attachment_ids': [(6, 0, attachment_ids)]})
        vals = {'mail_id': mail.id}
        return vals

    def validate_phone(self):
        self.ensure_one()
        assert self.reminder_type == 'phone'
        vals = {
            'result_id': self.result_id.id or False,
            'result_notes': self.result_notes,
            }
        return vals

    def validate_post(self):
        self.ensure_one()
        assert self.reminder_type == 'post'
        if not self.letter_printed:
            raise UserError(_(
                "Remind letter hasn't been printed!"))
        return {}

    def _prepare_overdue_reminder_action(self, vals):
        vals.update({
            'user_id': self.user_id.id,
            'reminder_type': self.reminder_type,
            'reminder_ids': [],
            'company_id': self.company_id.id,
            'commercial_partner_id': self.commercial_partner_id.id,
            'partner_id': self.partner_id.id,
            })
        for inv in self.invoice_ids:
            rvals = {'invoice_id': inv.id}
            if self.reminder_type != 'phone':
                rvals['counter'] = inv.overdue_reminder_counter + 1
            vals['reminder_ids'].append((0, 0, rvals))

    def print_letter(self):
        self.check_warnings()
        self.write({'letter_printed': True})
        action = self.env['report'].get_action(
            self, 'account_invoice_overdue_reminder.report_overdue_reminder')
        return action

    def print_invoices(self):
        # in v12, it seems printing several invoices at the same time
        # doesn't work
        action = self.env['report'].get_action(
            self.invoice_ids, 'account.report_invoice')
        return action

    def total_residual(self):
        self.ensure_one()
        res = {}
        for inv in self.invoice_ids:
            if inv.currency_id in res:
                res[inv.currency_id] += inv.residual_signed
            else:
                res[inv.currency_id] = inv.residual_signed
        return res.items()


class OverdueReminderEnd(models.TransientModel):
    _name = 'overdue.reminder.end'
    _description = 'Congratulation end screen for overdue reminder wizard'


class OverdueRemindMassUpdate(models.TransientModel):
    _name = 'overdue.reminder.mass.update'
    _description = 'Update several actions at the same time'

    update_action = fields.Selection([
        ('validate', 'Validate'),
        ('reminder_type', 'Change Reminder Type'),
        ('skip', 'Skip')],
        required=True, readonly=True)
    reminder_type = fields.Selection(
        '_reminder_type_selection',
        string='New Reminder Type')

    @api.model
    def _reminder_type_selection(self):
        return self.env['overdue.reminder.action']._reminder_type_selection()

    def run(self):
        self.ensure_one()
        assert self._context.get('active_model') == 'overdue.reminder.step'
        actions = self.env['overdue.reminder.step'].browse(
            self._context.get('active_ids'))
        if self.update_action == 'validate':
            actions.validate()
        elif self.update_action == 'skip':
            actions.skip()
        elif self.update_action == 'reminder_type':
            if not self.reminder_type:
                raise UserError(_("You must select the new reminder type."))
            actions.write({'reminder_type': self.reminder_type})
        return
