from flask import render_template

from src.editor.operations.operation import Operation


class Neighbors(Operation):
    @classmethod
    def name(cls):
        return "neighbors"

    @classmethod
    def template(cls):
        return "= <R#<ROW>-1:<ROW>-1><C#<COL>-1:<COL>> + <R#<ROW>-1:<ROW>><C#<COL>+1:<COL>+1> + <R#<ROW>+1:<ROW>+1><C#<COL>:<COL>+1> + <R#<ROW>:<ROW>+1><C#<COL>-1:<COL>-1>"

    @classmethod
    def render(cls):
        return render_template(
                "partials/editor/operations/generic.html",
                operation=cls.name(),
                show=True,
        )
