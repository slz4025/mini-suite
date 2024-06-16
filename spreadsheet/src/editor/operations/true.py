from flask import render_template

from src.editor.operations.operation import Operation


class TrueOp(Operation):
    @classmethod
    def name(cls):
        return "true"

    @classmethod
    def template(cls):
        return "True"

    @classmethod
    def render(cls):
        return render_template(
                "partials/editor/operations/generic.html",
                operation=cls.name(),
                show=True,
        )
