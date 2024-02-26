from dataclasses import dataclass
from flask import render_template
import os
import re
from typing import Callable

from src.errors import ClientError, UserError
from src.form import extract, parse_int, validate_bounds, validate_nonempty
from src.modes import check_mode
from src.sheet import (
    Axis,
    Range,
    BoxSelection,
    RangeSelection,
    IndicesSelection,
    Selection,
    InsertInput,
    ValueInput,
    Input,
    Modification,
    get_bounds,
    get_indices,
    set_range,
)


def validate_range(axis, r):
    start, end = set_range(axis, r)

    bounds = get_bounds()
    match axis:
        case Axis.ROW:
            bound = bounds.row
            name = "Row"
        case Axis.COLUMN:
            bound = bounds.col
            name = "Column"

    validate_bounds(start, 0, bound, name="start")
    validate_bounds(end, 0, bound, name="end")

    if end < start:
        raise UserError(
            f"{name} end, {end}, is less than start, {start}."
        )


def get_all_indices(axis, ranges):
    all_indices = []
    for r in ranges:
        start, end = set_range(axis, r)
        indices = get_indices(start, end)
        all_indices.extend(indices)
    return list(set(all_indices))


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
            raise UserError(
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


def validate_and_parse_row_range(form):
    start = extract(form, "selection-start", name="start")
    start = None if start == "" else parse_int(start, name="start")
    end = extract(form, "selection-end", name="end")
    end = None if end == "" else parse_int(end, name="end")
    r = Range(start=start, end=end)
    validate_range(axis=Axis.ROW, r=r)
    sel = RangeSelection(axis=Axis.ROW, range=r)
    return sel


def validate_and_parse_col_range(form):
    start = extract(form, "selection-start", name="start")
    start = None if start == "" else parse_int(start, name="start")
    end = extract(form, "selection-end", name="end")
    end = None if end == "" else parse_int(end, name="end")
    r = Range(start=start, end=end)
    validate_range(axis=Axis.COLUMN, r=r)
    sel = RangeSelection(axis=Axis.COLUMN, range=r)
    return sel


def validate_and_parse_row_indices(form):
    query = extract(form, "selection-query", name="query")
    ranges = validate_and_parse_ranges(query)
    for r in ranges:
        validate_range(axis=Axis.ROW, r=r)
    indices = get_all_indices(axis=Axis.ROW, ranges=ranges)
    sel = IndicesSelection(axis=Axis.ROW, indices=indices)
    return sel


def validate_and_parse_col_indices(form):
    query = extract(form, "selection-query", name="query")
    ranges = validate_and_parse_ranges(query)
    for r in ranges:
        validate_range(axis=Axis.COLUMN, r=r)
    indices = get_all_indices(axis=Axis.COLUMN, ranges=ranges)
    sel = IndicesSelection(axis=Axis.COLUMN, indices=indices)
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
    validate_range(axis=Axis.ROW, r=row_range)
    col_range = Range(start=sc, end=ec)
    validate_range(axis=Axis.COLUMN, r=col_range)

    sel = BoxSelection(rows=row_range, cols=col_range)
    return sel


@dataclass
class SelectionMode:
    name: str
    template: str
    validate_and_parse: Callable[[object], Selection]


selection_modes = {
    "Box": SelectionMode(
        name="Box",
        template="box.html",
        validate_and_parse=validate_and_parse_box,
    ),
    "Rows (Range)": SelectionMode(
        name="Rows (Range)",
        template="range.html",
        validate_and_parse=validate_and_parse_row_range,
    ),
    "Columns (Range)": SelectionMode(
        name="Columns (Range)",
        template="range.html",
        validate_and_parse=validate_and_parse_col_range,
    ),
    "Rows (Indices)": SelectionMode(
        name="Rows (Indices)",
        template="indices.html",
        validate_and_parse=validate_and_parse_row_indices,
    ),
    "Columns (Indices)": SelectionMode(
        name="Columns (Indices)",
        template="indices.html",
        validate_and_parse=validate_and_parse_col_indices,
    ),
}


def get_selection_mode(name):
    if name in selection_modes:
        return selection_modes[name]
    else:
        raise ClientError(f"Unknown selection mode: {name}.")


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
            axis = Axis.ROW
            bound = bounds.row
        case "Column":
            axis = Axis.COLUMN
            bound = bounds.col
        case _:
            raise ClientError(f"Name '{axis_name}' is not a valid axis.")

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
        raise UserError("Field 'value' was not given.")

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
    selection_mode_options = [
        "Rows (Range)",
        "Columns (Range)",
        "Rows (Indices)",
        "Columns (Indices)",
    ]
    selection_form = render_selection(session, selection_mode_options)
    return render_template(
            "partials/bulk_edit/delete.html",
            selection_form=selection_form,
    )


def render_erase_selection(session):
    selection_mode_options = [
        "Box",
        "Rows (Range)",
        "Columns (Range)",
        "Rows (Indices)",
        "Columns (Indices)",
    ]
    selection_form = render_selection(session, selection_mode_options)
    return render_template(
            "partials/bulk_edit/erase.html",
            selection_form=selection_form,
    )


def render_value_inputs(session):
    selection_mode_options = [
        "Box",
        "Rows (Range)",
        "Columns (Range)",
        "Rows (Indices)",
        "Columns (Indices)",
    ]
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
        raise ClientError(f"Operation {operation} not supported in bulk edit.")
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
