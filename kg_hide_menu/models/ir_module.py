# -*- coding: utf-8 -*-

# Klystron Global LLC
# Copyright (C) Klystron Global LLC
# All Rights Reserved
# https://www.klystronglobal.com/


from odoo import models, api, tools


class Menu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        menus = super(Menu, self)._visible_menu_ids(debug)
        if self.env.user.has_group('kg_hide_menu.group_hide_contacts'):
            menus.discard(335)
        if self.env.user.has_group('kg_hide_menu.group_account_vendors'):
            menus.discard(123)
        if self.env.user.has_group('kg_hide_menu.group_hide_inv_overview_salesperson'):
            menus.discard(297)
        if self.env.user.hide_menu_access_ids:
            for rec in self.env.user.hide_menu_access_ids:
                menus.discard(rec.id)
            return menus
        return menus
