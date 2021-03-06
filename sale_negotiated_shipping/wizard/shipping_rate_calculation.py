# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Serpent Consulting Services PVT. LTD. (<http://www.serpentcs.com>) 
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp import models, fields, api

class shipping_rate_wizard(models.TransientModel):
    _name = "shipping.rate.wizard"
    _description = "Calculates shipping charges"
                
    shipping_cost = fields.Float(string='Shipping Cost')
    account_id = fields.Many2one('account.account', string='Account')
    rate_select = fields.Many2one('shipping.rate.config', string='Shipping Method')

    @api.model
    def update_shipping_cost(self):
        """
        Function to update sale order and invoice with new shipping cost and method
        """
        ids = self._ids
        context = self._context
        datas = self.browse(ids)
        if context is None:
            context = {}
        if context.get('active_model', False) in ['sale.order', 'account.invoice'] and 'active_id' in context:
            model = context['active_model']
            model_obj = self.env[model]
            model_id = context.get('active_id', False)
            model_browse = model_obj.browse(model_id)
            if model_id:
                model_browse.write({
                    'shipcharge': datas.shipping_cost,
                    'ship_method': datas.rate_select.shipmethodname,
                    'sale_account_id': datas.account_id.id,
                    'ship_method_id': datas.rate_select.id,
                    })
            if model == 'sale.order':
                model_browse.button_dummy()
            if model == 'account.invoice':
                model_browse.button_reset_taxes()
            return {'nodestroy': False, 'type': 'ir.actions.act_window_close'}

    @api.multi
    def onchange_shipping_method(self, rate_config_id):
        ret = {}
        ids = self._ids
        context = self._context
        if context is None:
            context = {}
        rate_config_obj = self.env['shipping.rate.config']
        rate_obj = self.env['shipping.rate']
        if context.get('active_model', False) in ['sale.order', 'account.invoice'] and 'active_id' in context:
            cost = 0.0 
            rate_config = rate_config_obj.browse(rate_config_id)
            account_id = rate_config.account_id and rate_config.account_id.id or False
            model = context['active_model']
            model_obj = self.env[model].browse(context['active_id'])
            
            # search adress partner 
           
            
            # TODO : find delivery address
            # get adresse customer
            # self._cr.execute('select type,id from res_partner where company_id = %s', (tuple([model_obj.company_id.id])))
            # res = self._cr.fetchall()
            # address = dict(res)
            # if address:
                # address_id = address.get('delivery', False) or address.get('default', False) or\
                             # address.values() and address.values()[0]
                # address_obj = self.env['res.partner'].browse(address_id)
                # if address_obj:
                
            print '----model_obj.partner_id-----------', model_obj.partner_id
            cost = rate_obj.find_cost(rate_config_id, model_obj.partner_id, model_obj)
            ret = {'value': {'shipping_cost': cost, 'account_id': account_id}}
        return ret


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
