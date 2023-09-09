from odoo import models, _
import base64


class StockPickingBatch(models.Model):
    _inherit = ["stock.picking.batch"]

    def action_confirm(self):
        super().action_confirm()
        self.send_mail()

    def send_mail(self):
        # Create pdf binary file
        report = self.env.ref("biba_ardoak.action_report_picking_batch_delivery_note")
        report_binary = report._render_qweb_pdf([self.id])
        email_to = self.env["ir.config_parameter"].get_param(
            "biba_ardoak.storehouse_email"
        )
        pdf = base64.encodebytes(report_binary[0])

        # Add attachment as email value
        email_values = {
            "email_to": email_to,
            "attachments": [[_("Delivery Note"), pdf]],
        }

        # Get email template
        template_id = self.env.ref(
            "biba_ardoak.delivery_note_mail_template_form_view"
        ).id
        template = self.env["mail.template"].browse(template_id)
        template.send_mail(self.id, email_values=email_values, force_send=True)

        # Save attachment sent by email
        name = _("Delivery Note")
        att = self.env["ir.attachment"].create(
            {
                "name": name,
                "type": "binary",
                "datas": pdf,
                "store_fname": name + ".pdf",
                "res_model": self._name,
                "res_id": self.id,
                "mimetype": "application/x-pdf",
            }
        )

        # Add template and attachment to chatter message
        self.message_post_with_template(template_id, attachment_ids=[att.id])
