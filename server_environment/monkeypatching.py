# Copyright 2025 Dynapps - Eric Lembregts
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.orm import model_classes

add_to_registry_original = model_classes.add_to_registry


def add_to_registry(registry, model_def):
    model_cls = add_to_registry_original(registry, model_def)
    # Only server.config defines the argument-less ``_build_model`` hook this patch
    # was written for. Other models may define their own ``_build_model`` with a
    # different signature (e.g. spec_driven_model's ``_build_model(pool, cr)``):
    # calling it for every model breaks the registry as soon as this module is
    # imported - and queue_job imports it opportunistically.
    if getattr(model_cls, "_name", None) == "server.config" and hasattr(
        model_cls, "_build_model"
    ):
        model_cls._build_model()
    return model_cls


# Monkey-patching of the method
model_classes.add_to_registry = add_to_registry
