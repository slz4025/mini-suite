from flask import render_template

from src.editor.operations.true import TrueOp
from src.editor.operations.false import FalseOp
from src.editor.operations.markdown import Markdown
from src.editor.operations.formula import Formula
from src.editor.operations.neighbors import Neighbors
from src.editor.operations.selection import Selection

operations = [
    TrueOp,
    FalseOp,
    Markdown,
    Formula,
    Neighbors,
    Selection,
]
operations_map = {o.name(): o for o in operations}


def get_value(op_name):
    operation = operations_map[op_name]
    value = operation.template()
    return value


def render():
    operations_html = "\n".join([v.render() for k, v in operations_map.items()])
    return render_template(
            "partials/editor/operations.html",
            operations=operations_html,
    )
