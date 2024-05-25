from enum import Enum
from dataclasses import dataclass
from flask import render_template

import src.errors as errors
import src.selection.modes as sel_modes
import src.selection.state as sel_state
import src.selection.types as sel_types


def get_show_operations(session):
    sel = sel_state.get_selection(session)
    if isinstance(sel, sel_types.RowRange):
        return True
    elif isinstance(sel, sel_types.ColRange):
        return True
    elif isinstance(sel, sel_types.Box):
        return True
    else:
        return False


def get_selection_macro(session):
    sel = sel_state.get_selection(session)
    if isinstance(sel, sel_types.RowRange):
        return "<R#{}:{}>".format(sel.start.value, sel.end.value-1)
    elif isinstance(sel, sel_types.ColRange):
        return "<C#{}:{}>".format(sel.start.value, sel.end.value-1)
    elif isinstance(sel, sel_types.Box):
        return "<R#{}:{}><C#{}:{}>".format(
            sel.row_range.start.value, sel.row_range.end.value-1,
            sel.col_range.start.value, sel.col_range.end.value-1,
        )
    else:
        sel_mode = sel_modes.from_selection(sel)
        raise errors.NotSupportedError(
            "Selection mode {} is not supported in formulas."
            .format(sel_mode.value)
        )


class Name(Enum):
    SUM = "Sum"
    AVERAGE = "Average"


@dataclass
class Operation:
    name: Name
    template: str


all_operations = {
    Name.SUM: Operation(
        name=Name.SUM,
        template="=sum({sel_macro})",
    ),
    Name.AVERAGE: Operation(
        name=Name.AVERAGE,
        template="=float(sum([e for e in {sel_macro}])) "
        + "/ float(len({sel_macro}))",
    ),
}


def from_input(name_str):
    match name_str:
        case "Sum":
            return Name.SUM
        case "Average":
            return Name.AVERAGE
        case _:
            raise errors.UnknownOptionError(
                f"Unknown operation: {name_str}."
            )


def get_operation(op_name):
    if op_name not in all_operations:
        raise errors.UnknownOptionError(f"Unknown operation: {op_name.value}.")
    return all_operations[op_name]


def get_formula_with_selection(session, op_name):
    operation = get_operation(op_name)
    template = operation.template

    sel_macro = get_selection_macro(session)
    formula = template.format(sel_macro=sel_macro)
    return formula


def render(session):
    show_operations = get_show_operations(session)
    return render_template(
            "partials/editor/operations.html",
            show_operations=show_operations,
    )
