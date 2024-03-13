from odoo import api, fields, models, SUPERUSER_ID, _

import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import AccessError, UserError, ValidationError
from lxml import etree

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    CUSTOM_FIELD_STATES = {
        state: [('readonly', False)]
        for state in {'sale', 'done', 'cancel'}
    }

    
    date_order = fields.Datetime(string="Order Date",states=CUSTOM_FIELD_STATES,copy=False, track_visibility="onchange")
    p_o_ref = fields.Char(string='Custom PO Reference')
    custom_salesperson_id = fields.Many2one('custom.salesperson',string='Custom Salesperson.', tracking=2)
    # logistic_duration_id =  fields.Many2one('customer.logistic.timing',string='Logistic Timing',related='partner_id.customer_logistic_id',tracking=2,copy=False)
    customer_category_id =  fields.Many2one('customer.catgeory',string='Customer Category',related='partner_id.customer_category_id',tracking=2,copy=False)
    customer_remarks =  fields.Text(string='Customer Remarks',related='partner_id.cus_remarks', tracking=2,copy=False)
    is_accessed_sp = fields.Boolean(string="Is accessed salesperson", compute='_compute_accessed_salesperson')

    def _compute_accessed_salesperson(self):
        for rec in self:
            group_salesperson = self.env.ref('saam_extension.group_custom_sales_person')
            rec.is_accessed_sp = group_salesperson in self.env.user.groups_id
            
    def action_confirm(self):
        res = super(SaleOrder,self).action_confirm()
        if self.is_accessed_sp:
            raise UserError("You are not allowed to confirm the SO")
        return res

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['p_o_ref'] = self.p_o_ref
        invoice_vals['custom_salesperson_id'] = self.custom_salesperson_id.id 
        # invoice_vals['logistic_duration_id'] = self.logistic_duration_id.id 
        invoice_vals['customer_category_id'] = self.customer_category_id.id 
        invoice_vals['customer_remarks'] = self.customer_remarks
        return invoice_vals

    @api.onchange('partner_id')
    def onchange_partner_id_custom_sales_person(self): 
        if self.partner_id: 
            self.custom_salesperson_id = self.partner_id.custom_salesperson_id.id if self.partner_id.custom_salesperson_id else False

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    prod_boxes = fields.Text(string='Boxes')

    def _prepare_invoice_line(self, **optional_values):
        values = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        values.update({'prod_boxes':self.prod_boxes if self.prod_boxes else False})
        return values

    # 1.This fucntion will pass the P&D value from SO Line To Stock Move P&D Line

    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        values.update({'prod_boxes':self.prod_boxes if self.prod_boxes else False})
        print(values)
        return values

class StockMove(models.Model):
    _inherit = "stock.move"

    prod_boxes = fields.Text(string='Boxes')


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        res = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, company_id,values)
        res.update({'prod_boxes': values.get('prod_boxes') if values.get('prod_boxes') else False})
        return res

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    prod_boxes = fields.Text(related='move_id.prod_boxes',string='Boxes')
    
