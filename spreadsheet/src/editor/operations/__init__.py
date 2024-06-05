from flask import render_template

import src.errors.types as err_types
import src.selector.modes as sel_modes
import src.selector.state as sel_state
import src.selector.types as sel_types

import src.editor.operations.types as types


all_operations = {
    types.Name.SUM: types.Operation(
        name=types.Name.SUM,
        template="=sum({sel_macro})",
    ),
    types.Name.AVERAGE: types.Operation(
        name=types.Name.AVERAGE,
        template="=float(sum([e for e in {sel_macro}])) "
        + "/ float(len({sel_macro}))",
    ),
}


def from_input(name_str):
    match name_str:
        case "Sum":
            return types.Name.SUM
        case "Average":
            return types.Name.AVERAGE
        case _:
            raise err_types.UnknownOptionError(
                f"Unknown operation: {name_str}."
            )


def get_operation(op_name):
    if op_name not in all_operations:
        raise err_types.UnknownOptionError(f"Unknown operation: {op_name.value}.")
    return all_operations[op_name]


def show_operations(session):
    sel = sel_state.get_selection(session)
    if isinstance(sel, sel_types.RowRange):
        return True
    elif isinstance(sel, sel_types.ColRange):
        return True
    elif isinstance(sel, sel_types.Box):
        return True
    else:
        return False


def get_selection_macro(sel):
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
        raise err_types.NotSupportedError(
            "Selection mode {} is not supported in formulas."
            .format(sel_mode.value)
        )


def get_formula_with_selection(session, op_name):
    operation = get_operation(op_name)
    template = operation.template

    sel = sel_state.get_selection(session)
    sel_macro = get_selection_macro(sel)
    formula = template.format(sel_macro=sel_macro)
    return formula


def render(session):
    show_ops = show_operations(session)
    return render_template(
            "partials/editor/operations.html",
            show_operations=show_ops,
    )
