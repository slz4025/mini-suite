from flask import render_template

import src.errors.types as err_types

import src.bulk_editor.modifications as modifications
from src.bulk_editor.operations.operation import Operation


class Reverse(Operation):
    @classmethod
    def name(cls):
        return "Reverse"

    @classmethod
    def icon(cls):
        return ""

    @classmethod
    def validate_selection(cls, use, sel):
        raise err_types.NotSupported("Reverse does not accept selections.")

    @classmethod
    def apply(cls, form):
        modifications.apply_transaction(
            modifications.Transaction(
                modification_name="REVERSE",
                input=modifications.ReverseInput(),
            )
        )

    @classmethod
    def render(cls):
        return render_template(
                "partials/bulk_editor/reverse.html",
        )
