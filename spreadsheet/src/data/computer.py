import re

import src.data.sheet as sheet
import src.data.operations as operations
import src.errors as errors
import src.selection.types as sel_types


def is_formula(formula):
    return isinstance(formula, str) and formula.startswith("=")


def evaluate(expression):
    try:
        value = eval(expression)
    except Exception as e:
        raise errors.UserError(
            f"Evaluation of expression encountered error: {e}.\n"
            f"Expression: {expression}"
        )
    return value


def compute(cell_position, formula):
    if not is_formula(formula):
        value = formula
    else:
        formula = formula.removeprefix("=")
        formula = compile_position_references(cell_position, formula)
        formula = compile_selections(formula)
        formula = compile_castings(formula)
        value = evaluate(formula)
    return value


def replace_instances(formula, instances, replace_instance):
    offset = 0
    for instance in instances:
        value = replace_instance(instance)

        start_index = instance.start(0) + offset
        end_index = instance.end(0) + offset
        formula = formula[:start_index] + value + formula[end_index:]

        value_len = len(value)
        orig_len = end_index - start_index
        offset += value_len - orig_len

    return formula


def compile_position_references(cell_position, formula):
    curr_row_instances = re.finditer(r"CURR_ROW", formula)

    def curr_row_replace(instance):
        row = cell_position.row_index.value
        compiled = f"{row}"
        return compiled

    formula = replace_instances(formula, curr_row_instances, curr_row_replace)

    curr_col_instances = re.finditer(r"CURR_COL", formula)

    def curr_col_replace(instance):
        col = cell_position.col_index.value
        compiled = f"{col}"
        return compiled

    formula = replace_instances(formula, curr_col_instances, curr_col_replace)

    return formula


expression_regex = r"[^\<\>\n\r]+"


def compile_selections(formula):
    box_instances = re.finditer(
            r"BOX\<"
            + r"(?P<row_start>{}):".format(expression_regex)
            + r"(?P<row_end>{}),".format(expression_regex)
            + r"(?P<col_start>{}):".format(expression_regex)
            + r"(?P<col_end>{})".format(expression_regex)
            + r"\>",
            formula,
            )

    def box_replace(instance):
        row_start = evaluate(instance.group("row_start"))
        row_end = evaluate(instance.group("row_end"))
        col_start = evaluate(instance.group("col_start"))
        col_end = evaluate(instance.group("col_end"))
        sel = sel_types.Box(
            row_range=sel_types.RowRange(
                start=sheet.Index(row_start),
                end=sheet.Bound(row_end),
            ),
            col_range=sel_types.ColRange(
                start=sheet.Index(col_start),
                end=sheet.Bound(col_end),
            ),
        )
        arr = operations.get_box_values(sel)
        arr = [f"\"{e}\"" for e in arr]
        compiled = "[{}]".format(",".join(arr))
        return compiled

    formula = replace_instances(
        formula,
        box_instances,
        box_replace,
    )

    row_range_instances = re.finditer(
            r"ROWS\<"
            + r"(?P<row_start>{}):".format(expression_regex)
            + r"(?P<row_end>{})".format(expression_regex)
            + r"\>",
            formula,
            )

    def row_range_replace(instance):
        row_start = evaluate(instance.group("row_start"))
        row_end = evaluate(instance.group("row_end"))
        sel = sel_types.RowRange(
            start=sheet.Index(row_start),
            end=sheet.Bound(row_end),
        )
        arr = operations.get_row_range_values(sel)
        arr = [f"\"{e}\"" for e in arr]
        compiled = "[{}]".format(",".join(arr))
        return compiled

    formula = replace_instances(
        formula,
        row_range_instances,
        row_range_replace,
    )

    col_range_instances = re.finditer(
            r"COLS\<"
            + r"(?P<col_start>{}):".format(expression_regex)
            + r"(?P<col_end>{})".format(expression_regex)
            + r"\>",
            formula,
            )

    def col_range_replace(instance):
        col_start = evaluate(instance.group("col_start"))
        col_end = evaluate(instance.group("col_end"))
        sel = sel_types.ColRange(
            start=sheet.Index(col_start),
            end=sheet.Bound(col_end),
        )
        arr = operations.get_col_range_values(sel)
        arr = [f"\"{e}\"" for e in arr]
        compiled = "[{}]".format(",".join(arr))
        return compiled

    formula = replace_instances(
        formula,
        col_range_instances,
        col_range_replace,
    )

    return formula


def compile_castings(formula):
    int_instances = re.finditer(
            r"INT\<"
            + r"(?P<contents>{})".format(expression_regex)
            + r"\>",
            formula,
            )

    def int_replace(instance):
        contents = instance.group("contents")
        compiled = f"[int(float(e)) for e in {contents}]"
        return compiled

    formula = replace_instances(
        formula,
        int_instances,
        int_replace,
    )

    float_instances = re.finditer(
            r"FLOAT\<"
            + r"(?P<contents>{})".format(expression_regex)
            + r"\>",
            formula,
            )

    def float_replace(instance):
        contents = instance.group("contents")
        compiled = f"[float(e) for e in {contents}]"
        return compiled

    formula = replace_instances(
        formula,
        float_instances,
        float_replace,
    )

    return formula
