from flask import render_template

from src.editor.operations.operation import Operation


class FalseOp(Operation):
    @classmethod
    def name(cls):
        return "false"

    @classmethod
    def template(cls):
        return "False"

    @classmethod
    def render(cls):
        return render_template(
                "partials/editor/operations/generic.html",
                operation=cls.name(),
                show=True,
        )
