import src.errors as errors
import src.selection.modes as modes
import src.selection.types as types
import src.data.sheet as sheet


def is_row_header(cell_position):
    return cell_position.col_index.value == -1


def is_col_header(cell_position):
    return cell_position.row_index.value == -1


def compute_from_endpoints(start, end):
    actual_row_start = sheet.Index(
        min(start.row_index.value, end.row_index.value)
    )
    actual_row_end = sheet.Bound(
        max(start.row_index.value, end.row_index.value) + 1
    )
    actual_col_start = sheet.Index(
        min(start.col_index.value, end.col_index.value)
    )
    actual_col_end = sheet.Bound(
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
            raise errors.NotSupportedError(
                "Selection start is row header "
                "but selection end is col header."
            )
        else:
            raise errors.NotSupportedError(
                "Selection start is row header "
                "but selection end is cell."
            )
    elif is_col_header(start):
        if is_row_header(end):
            raise errors.NotSupportedError(
                "Selection start is col header "
                "but selection end is row header."
            )
        elif is_col_header(end):
            sel = types.ColRange(
                start=actual_col_start,
                end=actual_col_end,
            )
        else:
            raise errors.NotSupportedError(
                "Selection start is col header "
                "but selection end is cell."
            )
    else:
        if is_row_header(end):
            raise errors.NotSupportedError(
                "Selection start is cell "
                "but selection end is row header."
            )
        elif is_col_header(end):
            raise errors.NotSupportedError(
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
