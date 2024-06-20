import src.errors.types as err_types
import src.sheet as sheet
import src.sheet.types as sheet_types

import src.selector.checkers as checkers
import src.selector.types as types


def is_row_header(cell_position):
    return cell_position.col_index.value == -1


def is_col_header(cell_position):
    return cell_position.row_index.value == -1


def compute_from_endpoints(start, end):
    actual_row_start = sheet_types.Index(
        min(start.row_index.value, end.row_index.value)
    )
    actual_row_end = sheet_types.Bound(
        max(start.row_index.value, end.row_index.value) + 1
    )
    actual_col_start = sheet_types.Index(
        min(start.col_index.value, end.col_index.value)
    )
    actual_col_end = sheet_types.Bound(
        max(start.col_index.value, end.col_index.value) + 1
    )

    sel = None
    if is_row_header(start):
        if is_row_header(end):
            sel = types.RowRange(
                start=actual_row_start,
                end=actual_row_end,
            )
        elif is_col_header(end):
            raise err_types.NotSupportedError(
                "Selection start is row header "
                "but selection end is col header."
            )
        else:
            raise err_types.NotSupportedError(
                "Selection start is row header "
                "but selection end is cell."
            )
    elif is_col_header(start):
        if is_row_header(end):
            raise err_types.NotSupportedError(
                "Selection start is col header "
                "but selection end is row header."
            )
        elif is_col_header(end):
            sel = types.ColRange(
                start=actual_col_start,
                end=actual_col_end,
            )
        else:
            raise err_types.NotSupportedError(
                "Selection start is col header "
                "but selection end is cell."
            )
    else:
        if is_row_header(end):
            raise err_types.NotSupportedError(
                "Selection start is cell "
                "but selection end is row header."
            )
        elif is_col_header(end):
            raise err_types.NotSupportedError(
                "Selection start is cell "
                "but selection end is col header."
            )
        else:
            sel = types.Box(
                row_range=types.RowRange(
                    start=actual_row_start,
                    end=actual_row_end,
                ),
                col_range=types.ColRange(
                    start=actual_col_start,
                    end=actual_col_end,
                ),
            )

    return sel


def compute_updated_selection(sel, direction):
    bounds = sheet.data.get_bounds()
    max_row = bounds.row.value
    max_col = bounds.col.value

    if sel is None:
        return None
    elif isinstance(sel, types.Box):
        start_row = sel.row_range.start.value
        start_col = sel.col_range.start.value
        end_row = sel.row_range.end.value
        end_col = sel.col_range.end.value
        match direction:
            case 'up':
                end_row = max(start_row + 1, end_row - 1)
            case 'down':
                end_row = min(max_row, end_row + 1)
            case 'left':
                end_col = max(start_col + 1, end_col - 1)
            case 'right':
                end_col = min(max_col, end_col + 1)
            case _:
                raise err_types.UnknownOptionError(
                    f"Unexpected direction to modify selection: {direction}."
                )
        return types.Box(
            row_range=types.RowRange(
                start=sheet_types.Index(start_row),
                end=sheet_types.Bound(end_row),
            ),
            col_range=types.ColRange(
                start=sheet_types.Index(start_col),
                end=sheet_types.Bound(end_col),
            ),
        )
    elif isinstance(sel, types.RowRange):
        start_row = sel.start.value
        end_row = sel.end.value
        match direction:
            case 'up':
                end_row = max(start_row + 1, end_row - 1)
            case 'down':
                end_row = min(max_row, end_row + 1)
        return types.RowRange(
            start=sheet_types.Index(start_row),
            end=sheet_types.Bound(end_row),
        )
    elif isinstance(sel, types.ColRange):
        start_col = sel.start.value
        end_col = sel.end.value
        match direction:
            case 'left':
                end_col = max(start_col + 1, end_col - 1)
            case 'right':
                end_col = min(max_col, end_col + 1)
        return types.ColRange(
            start=sheet_types.Index(start_col),
            end=sheet_types.Bound(end_col),
        )
    else:
        return None


def get_bounds_from_selection(sel):
    row_range = checkers.check_and_set_row_range(
        types.RowRange(start=None, end=None),
    )
    row_start = row_range.start.value
    row_end = row_range.end.value

    col_range = checkers.check_and_set_col_range(
        types.ColRange(start=None, end=None),
    )
    col_start = col_range.start.value
    col_end = col_range.end.value

    if isinstance(sel, types.RowRange):
        row_start = sel.start.value
        row_end = sel.end.value
    elif isinstance(sel, types.ColRange):
        col_start = sel.start.value
        col_end = sel.end.value
    elif isinstance(sel, types.Box):
        row_start = sel.row_range.start.value
        row_end = sel.row_range.end.value
        col_start = sel.col_range.start.value
        col_end = sel.col_range.end.value
    else:
        raise err_types.NotSupportedError(
            f"Selection type, {type(sel)}, does not have bounds."
        )

    return row_start, row_end, col_start, col_end
