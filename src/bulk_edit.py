from dataclasses import dataclass
from flask import render_template
import os
import re
from typing import Callable

from src.form import extract, parse_int, validate_bounds, validate_nonempty
from src.modes import check_mode
from src.sheet import (
    Modification,
    Range,
    BoxSelection,
    IndexSelection,
    Selection,
    InsertInput,
    ValueInput,
    Input,
    get_bounds,
)


def validate_row_range(r):
    bound = get_bounds().row
    if r.start is not None:
        validate_bounds(r.start, 0, bound, name="row start")
    if r.end is not None:
        validate_bounds(r.end, 0, bound, name="row end")
    if r.start is not None and r.end is not None and r.end < r.start:
        raise Exception(
            f"Row end, {r.end}, is less than start, {r.start}."
        )


def validate_col_range(c):
    bound = get_bounds().col
    if c.start is not None:
        validate_bounds(c.start, 0, bound, name="col start")
    if c.end is not None:
        validate_bounds(c.end, 0, bound, name="col end")
    if c.start is not None and c.end is not None and c.end < c.start:
        raise Exception(
            f"Column end, {c.end}, is less than start, {c.start}."
        )


def get_row_indices(ranges):
    indices = []
    for r in ranges:
        start = 0 if r.start is None else r.start
        end = get_bounds().row if r.end is None else r.end
        indices.extend(list(range(start, end)))
    return list(set(indices))


def get_col_indices(ranges):
    indices = []
    for r in ranges:
        start = 0 if r.start is None else r.start
        end = get_bounds().col if r.end is None else r.end
        indices.extend(list(range(start, end)))
    return list(set(indices))


range_pattern = "^([0-9]*)(:[0-9]*)?$"
range_re = re.compile(range_pattern)


def validate_and_parse_ranges(query):
    entries = query.split(",")
    entries = [e.strip() for e in entries]
    entries = [e for e in entries if e != ""]
    ranges = []
    for e in entries:
        m = range_re.search(e)
        if not m:
            raise Exception(
                f"Pattern '{e}' does not match a valid index or range."
            )
        else:
            raw = m.groups()[0]
            first = None
            second = None
            if raw != "":
                first = parse_int(raw, "start")
                second = first+1

            raw = m.groups()[1]
            if raw is not None:
                raw = raw[1:]
                if raw != "":
                    second = parse_int(raw, "end")
                else:
                    second = None  # handles case like '1:'
            range = Range(first, second)
            ranges.append(range)

    if len(ranges) == 0:
        ranges.append(Range(None, None))

    return ranges


def validate_and_parse_rows(form):
    query = extract(form, "selection-query", name="query")
    ranges = validate_and_parse_ranges(query)
    for r in ranges:
        validate_row_range(r)
    indices = get_row_indices(ranges)
    sel = IndexSelection(axis=0, indices=indices)
    return sel


def validate_and_parse_cols(form):
    query = extract(form, "selection-query", name="query")
    ranges = validate_and_parse_ranges(query)
    for r in ranges:
        validate_col_range(r)
    indices = get_col_indices(ranges)
    sel = IndexSelection(axis=1, indices=indices)
    return sel


def validate_and_parse_box(form):
    sr = extract(form, "selection-sr", name="starting row")
    sr = None if sr == "" else parse_int(sr, name="starting row")
    er = extract(form, "selection-er", name="ending row")
    er = None if er == "" else parse_int(er, name="ending row")
    sc = extract(form, "selection-sc", name="starting column")
    sc = None if sc == "" else parse_int(sc, name="starting column")
    ec = extract(form, "selection-ec", name="ending column")
    ec = None if ec == "" else parse_int(ec, name="ending column")

    row_range = Range(start=sr, end=er)
    validate_row_range(row_range)
    col_range = Range(start=sc, end=ec)
    validate_col_range(col_range)

    sel = BoxSelection(rows=row_range, cols=col_range)
    return sel


@dataclass
class SelectionMode:
    name: str
    template: str
    validate_and_parse: Callable[[object], Selection]


selection_modes = {
    "Rows": SelectionMode(
        name="Rows",
        template="indices.html",
        validate_and_parse=validate_and_parse_rows,
    ),
    "Columns": SelectionMode(
        name="Columns",
        template="indices.html",
        validate_and_parse=validate_and_parse_cols,
    ),
    "Box": SelectionMode(
        name="Box",
        template="box.html",
        validate_and_parse=validate_and_parse_box,
    ),
}


def get_selection_mode(name):
    if name in selection_modes:
        return selection_modes[name]
    else:
        raise Exception(f"Unknown selection mode: {name}")


def validate_and_parse_selection(form):
    mode = extract(form, "selection-mode", name="selection mode")
    selection_mode = get_selection_mode(mode)
    selection = selection_mode.validate_and_parse(form)
    return selection


def validate_and_parse_insert_inputs(form):
    axis_name = extract(form, "insert-axis", name="axis")
    bounds = get_bounds()
    match axis_name:
        case "Row":
            axis = 0
            bound = bounds.row
        case "Column":
            axis = 1
            bound = bounds.col
        case _:
            raise Exception(f"'{axis_name}' is not a valid axis.")

    index = extract(form, "insert-index", name="index")
    validate_nonempty(index, name="index")
    index = parse_int(index, name="index")
    validate_bounds(index, 0, bound, name="index")

    number = extract(form, "insert-number", name="number")
    validate_nonempty(number, name="number")
    number = parse_int(number, name="number")
    return InsertInput(axis=axis, index=index, number=number)


def validate_and_parse_value_inputs(form):
    selection = validate_and_parse_selection(form)

    value = extract(form, "value", name="value")
    if value == "":
        raise Exception("Field 'value' was not given.")

    return ValueInput(selection=selection, value=value)


def render_insert_inputs(session):
    return render_template(
            "partials/bulk_edit/insert.html",
    )


def render_selection_inputs(session, mode):
    help_state = check_mode(session, "Help")
    selection_mode = get_selection_mode(mode)
    template_path = os.path.join(
        "partials/bulk_edit/selection",
        selection_mode.template,
    )
    html = render_template(template_path, show_help=help_state)
    return html


def render_selection(session, selection_mode_options):
    help_state = check_mode(session, "Help")
    default_selection_mode = selection_mode_options[0]
    selection_inputs = render_selection_inputs(session, default_selection_mode)
    return render_template(
            "partials/bulk_edit/selection.html",
            selection_mode=default_selection_mode,
            selection_mode_options=selection_mode_options,
            selection_inputs=selection_inputs,
            show_help=help_state,
    )


def render_delete_selection(session):
    selection_mode_options = ["Rows", "Columns"]
    selection_form = render_selection(session, selection_mode_options)
    return render_template(
            "partials/bulk_edit/delete.html",
            selection_form=selection_form,
    )


def render_erase_selection(session):
    selection_mode_options = ["Box", "Rows", "Columns"]
    selection_form = render_selection(session, selection_mode_options)
    return render_template(
            "partials/bulk_edit/erase.html",
            selection_form=selection_form,
    )


def render_value_inputs(session):
    selection_mode_options = ["Box", "Rows", "Columns"]
    selection_form = render_selection(session, selection_mode_options)
    return render_template(
            "partials/bulk_edit/value.html",
            value="",
            selection_form=selection_form,
    )


@dataclass
class OperationForm:
    validate_and_parse: Callable[[object], Input]
    render: Callable[[], str]


operation_forms = {
    "DELETE": OperationForm(
        validate_and_parse=validate_and_parse_selection,
        render=render_delete_selection,
    ),
    "INSERT": OperationForm(
        validate_and_parse=validate_and_parse_insert_inputs,
        render=render_insert_inputs,
    ),
    "ERASE": OperationForm(
        validate_and_parse=validate_and_parse_selection,
        render=render_erase_selection,
    ),
    "VALUE": OperationForm(
        validate_and_parse=validate_and_parse_value_inputs,
        render=render_value_inputs,
    ),
}


operation_options = sorted(operation_forms)
default_operation = operation_options[0]


def get_operation_form(operation):
    if operation not in operation_forms:
        raise Exception(f"Operation {operation} not supported in bulk edit.")
    operation_form = operation_forms[operation]
    return operation_form


def validate_and_parse(form):
    operation = extract(form, "operation")
    operation_form = get_operation_form(operation)
    operation_input = operation_form.validate_and_parse(form)
    modification = Modification(operation=operation, input=operation_input)
    return modification


def render_operation_form(session, operation):
    operation_form = get_operation_form(operation)
    return operation_form.render(session)


def render_controls(session):
    bulk_edit_state = check_mode(session, "Bulk-Edit")
    operation_form = render_operation_form(session, default_operation)

    return render_template(
            "partials/bulk_edit/controls.html",
            show_bulk_edit=bulk_edit_state,
            operation=default_operation,
            operation_options=operation_options,
            operation_form=operation_form,
    )