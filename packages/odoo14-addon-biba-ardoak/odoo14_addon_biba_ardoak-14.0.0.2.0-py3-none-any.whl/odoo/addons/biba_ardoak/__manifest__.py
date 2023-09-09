# pylint: disable=W0104
{
    "name": "Odoo Biba Ardoak customizations",
    "version": "14.0.0.2.0",
    "depends": ["base", "sale_stock", "stock_picking_batch", "sale", "product"],
    "author": "Coopdevs Treball SCCL",
    "website": "https://coopdevs.org",
    "category": "Cooperative management",
    "license": "AGPL-3",
    "data": [
        "data/ir_config_parameter.xml",
        "report/account_invoice_report_view.xml",
        "report/report_delivery_document_note.xml",
        "report/delivery_note_mail_template.xml",
        "report/report_picking_batch_delivery_note.xml",
        "report/stock_picking_batch_report_views.xml",
        "views/product_template.xml",
        "views/report_invoice.xml",
        "views/report_view.xml",
        "views/res_partner.xml",
        "wizards/stock_picking_batch/stock_picking_batch.xml",
        "security/ir.model.access.csv",
    ],
}
