from flask import render_template

import src.errors.types as err_types
import src.selector.modes as sel_modes
import src.selector.state as sel_state
import src.selector.types as sel_types

import src.editor.operations.types as types


def show_selection():
    sel = sel_state.get_selection()
    if isinstance(sel, sel_types.RowRange):
        return True
    elif isinstance(sel, sel_types.ColRange):
        return True
    elif isinstance(sel, sel_types.Box):
        return True
    else:
        return False


def get_selection_macro():
    sel = sel_state.get_selection()
    if isinstance(sel, sel_types.RowRange):
        macro = "<R#{}:{}>".format(sel.start.value, sel.end.value-1)
    elif isinstance(sel, sel_types.ColRange):
        macro = "<C#{}:{}>".format(sel.start.value, sel.end.value-1)
    elif isinstance(sel, sel_types.Box):
        macro = "<R#{}:{}><C#{}:{}>".format(
            sel.row_range.start.value, sel.row_range.end.value-1,
            sel.col_range.start.value, sel.col_range.end.value-1,
        )
    else:
        sel_mode = sel_modes.from_selection(sel)
        raise err_types.NotSupportedError(
            f"Selection mode {sel_mode.value} is not supported in formulas."
        )
    return macro


def render_operation(op_name):
    show = show_selection() if op_name == types.Name.SELECTION else True
    return render_template(
            "partials/editor/operations/generic.html",
            operation=op_name.value,
            show=show,
    )


all_operations = {
    types.Name.TRUE: types.Operation(
        name=types.Name.TRUE,
        template=lambda: "True",
    ),
    types.Name.FALSE: types.Operation(
        name=types.Name.FALSE,
        template=lambda: "False",
    ),
    types.Name.MARKDOWN: types.Operation(
        name=types.Name.MARKDOWN,
        template=lambda: "!**hello world**",
    ),
    types.Name.FORMULA: types.Operation(
        name=types.Name.FORMULA,
        template=lambda: "=1+2",
    ),
    types.Name.NEIGHBORS: types.Operation(
        name=types.Name.NEIGHBORS,
        template=lambda: "= <R#<ROW>-1:<ROW>-1><C#<COL>-1:<COL>> + <R#<ROW>-1:<ROW>><C#<COL>+1:<COL>+1> + <R#<ROW>+1:<ROW>+1><C#<COL>:<COL>+1> + <R#<ROW>:<ROW>+1><C#<COL>-1:<COL>-1>",
    ),
    types.Name.SELECTION: types.Operation(
        name=types.Name.SELECTION,
        template=lambda: "=" + get_selection_macro(),
    ),
}


def from_input(name_str):
    match name_str:
        case "true":
            return types.Name.TRUE
        case "false":
            return types.Name.FALSE
        case "markdown":
            return types.Name.MARKDOWN
        case "formula":
            return types.Name.FORMULA
        case "neighbors":
            return types.Name.NEIGHBORS
        case "selection":
            return types.Name.SELECTION
        case _:
            raise err_types.UnknownOptionError(
                f"Unknown editor operation: {name_str}."
            )


def get_operation(op_name):
    if op_name not in all_operations:
        raise err_types.UnknownOptionError(f"Unknown editor operation: {op_name.value}.")
    return all_operations[op_name]


def get_value(op_name):
    operation = get_operation(op_name)
    value = operation.template()
    return value


def render():
    operations_html = "\n".join([render_operation(op_name) for op_name in all_operations])
    return render_template(
            "partials/editor/operations.html",
            operations=operations_html,
    )
