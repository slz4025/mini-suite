from flask import render_template

from src.editor.operations.operation import Operation


class Formula(Operation):
    @classmethod
    def name(cls):
        return "formula"

    @classmethod
    def template(cls):
        return "=1+2"

    @classmethod
    def render(cls):
        return render_template(
                "partials/editor/operations/generic.html",
                operation=cls.name(),
                show=True,
        )
