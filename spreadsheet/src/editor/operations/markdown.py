from flask import render_template

from src.editor.operations.operation import Operation


class Markdown(Operation):
    @classmethod
    def name(cls):
        return "markdown"

    @classmethod
    def template(cls):
        return "!**hello world**"

    @classmethod
    def render(cls):
        return render_template(
                "partials/editor/operations/generic.html",
                operation=cls.name(),
                show=True,
        )
