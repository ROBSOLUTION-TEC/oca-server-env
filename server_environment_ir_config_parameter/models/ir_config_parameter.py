# Copyright 2016-2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError

from odoo.addons.base.models.ir_config_parameter import INVALID_VALUE
from odoo.addons.server_environment.server_env import serv_config

SECTION = "ir.config_parameter"


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    is_environment = fields.Boolean(
        string="Defined by environment",
        compute="_compute_is_environment",
        help="If check, the value in the database will be ignored"
        " and alternatively, the system will use the key defined"
        " in your odoo.cfg environment file.",
    )

    def _compute_is_environment(self):
        for parameter in self:
            parameter.is_environment = serv_config.has_option(SECTION, parameter.key)

    def _get(self, key, type_="str"):
        """Odoo 20 typed getters (get_str, get_bool, ...) read through ``_get``:
        a key defined in the server environment always wins over the database.

        Unlike the 19.0 version, the value is not written in the database on
        first access: ``_get`` is cached and must stay side-effect free.
        """
        value, id_ = super()._get(key, type_)
        if serv_config.has_option(SECTION, key):
            cvalue = serv_config.get(SECTION, key)
            if not cvalue:
                raise UserError(
                    self.env._("Key %s is empty in server_environment_file", key)
                )
            try:
                return self._convert(cvalue, type_), id_
            except ValueError:
                return INVALID_VALUE, id_
        return value, id_

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            key = vals.get("key")
            if key and serv_config.has_option(SECTION, key):
                # enforce value from config file
                vals.update(value=serv_config.get(SECTION, key))
        return super().create(vals_list)

    def write(self, vals):
        for rec in self:
            key = vals.get("key", rec.key)
            if serv_config.has_option(SECTION, key):
                # enforce value from config file
                newvals = dict(vals, value=serv_config.get(SECTION, key))
            else:
                newvals = vals
            super(IrConfigParameter, rec).write(newvals)
        return True
