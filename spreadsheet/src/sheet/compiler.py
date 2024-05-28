# Regex-based compiler of macros.

import re
from typing import List

import src.errors.types as err_types
import src.selector.types as sel_types
import src.sheet.data as sheet_data
import src.sheet.types as sheet_types


num_regex = r"[0-9]+"
expression_regex = r"[^\<\>\n\r]+"


class Node:
    def __init__(self, formula, dependencies):
        self.formula: str = formula
        self.dependencies: List[sel_types.CellPosition] = dependencies

    def add_dependency(self, position):
        index = len(self.dependencies)
        self.dependencies.append(position)
        return index

    def get_dependency(self, index):
        assert index >= 0 and index < len(self.dependencies)
        return self.dependencies[index]


# For compile-time evaluations, i.e. whatever is in macro.
def evaluate(cell_position, expression):
    try:
        value = eval(expression)
    except Exception as e:
        raise err_types.UserError(
            "Evaluation of expression at cell position "
            f"({cell_position.row_index.value}, "
            f"{cell_position.col_index.value}) "
            f"encountered error: {e}.\n"
            f"Expression: {expression}"
        )
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


def position_references(cell_position, node):
    formula = node.formula

    curr_row_instances = re.finditer(r"\<ROW\>", formula)

    def curr_row_replace(instance):
        row = cell_position.row_index.value
        compiled = f"{row}"
        return compiled

    formula = replace_instances(formula, curr_row_instances, curr_row_replace)

    curr_col_instances = re.finditer(r"\<COL\>", formula)

    def curr_col_replace(instance):
        col = cell_position.col_index.value
        compiled = f"{col}"
        return compiled

    formula = replace_instances(formula, curr_col_instances, curr_col_replace)

    node.formula = formula
    return node


def get_row_range_positions(sel):
    sel = sel_types.check_and_set_row_range(sel)
    bounds = sheet_data.get_bounds()

    pos = []
    for i in range(sel.start.value, sel.end.value):
        for j in range(0, bounds.col.value):
            pos.append(sel_types.CellPosition(
                row_index=sel_types.RowIndex(i),
                col_index=sel_types.ColIndex(j),
            ))
    return pos


def get_col_range_positions(sel):
    sel = sel_types.check_and_set_col_range(sel)
    bounds = sheet_data.get_bounds()

    pos = []
    for i in range(0, bounds.row.value):
        for j in range(sel.start.value, sel.end.value):
            pos.append(sel_types.CellPosition(
                row_index=sel_types.RowIndex(i),
                col_index=sel_types.ColIndex(j),
            ))
    return pos


def get_box_positions(sel):
    sel = sel_types.check_and_set_box(sel)

    pos = []
    for i in range(sel.row_range.start.value, sel.row_range.end.value):
        for j in range(sel.col_range.start.value, sel.col_range.end.value):
            pos.append(sel_types.CellPosition(
                row_index=sel_types.RowIndex(i),
                col_index=sel_types.ColIndex(j),
            ))
    return pos


def selections(cell_position, node):
    formula = node.formula

    # Compute box before row range and col range so compile properly.
    # expressions should not have :
    box_instances = re.finditer(
            r"\<R#"
            + r"(?P<row_start>{}):".format(expression_regex)
            + r"(?P<row_end>{})".format(expression_regex)
            + r"\>"
            + r"\<C#"
            + r"(?P<col_start>{}):".format(expression_regex)
            + r"(?P<col_end>{})".format(expression_regex)
            + r"\>",
            formula,
            )

    def box_replace(instance):
        row_start = evaluate(cell_position, instance.group("row_start"))
        row_end = evaluate(cell_position, instance.group("row_end"))
        col_start = evaluate(cell_position, instance.group("col_start"))
        col_end = evaluate(cell_position, instance.group("col_end"))
        sel = sel_types.Box(
            row_range=sel_types.RowRange(
                start=sheet_types.Index(row_start),
                # make exclusive
                end=sheet_types.Bound(row_end+1),
            ),
            col_range=sel_types.ColRange(
                start=sheet_types.Index(col_start),
                # make exclusive
                end=sheet_types.Bound(col_end+1),
            ),
        )
        pos = get_box_positions(sel)

        expr_arr = []
        for p in pos:
            r = node.add_dependency(p)
            expr = f"EVAL<{r}>"
            expr_arr.append(expr)
        compiled = "[{}]".format(",".join(expr_arr))

        return compiled

    formula = replace_instances(
        formula,
        box_instances,
        box_replace,
    )

    # Compute cell before row index and col index so compile properly.
    cell_instances = re.finditer(
            r"\<R#"
            + r"(?P<row>{})".format(expression_regex)
            + r"\>"
            + r"\<C#"
            + r"(?P<col>{})".format(expression_regex)
            + r"\>",
            formula,
            )

    def cell_replace(instance):
        row = evaluate(cell_position, instance.group("row"))
        col = evaluate(cell_position, instance.group("col"))
        sel = sel_types.Box(
            row_range=sel_types.RowRange(
                start=sheet_types.Index(row),
                end=sheet_types.Bound(row+1),
            ),
            col_range=sel_types.ColRange(
                start=sheet_types.Index(col),
                end=sheet_types.Bound(col+1),
            ),
        )
        pos = get_box_positions(sel)

        assert len(pos) == 1
        p = pos[0]
        r = node.add_dependency(p)
        compiled = f"EVAL<{r}>"

        return compiled

    formula = replace_instances(
        formula,
        cell_instances,
        cell_replace,
    )

    # expressions should not have :
    row_range_instances = re.finditer(
            r"\<R#"
            + r"(?P<row_start>{}):".format(expression_regex)
            + r"(?P<row_end>{})".format(expression_regex)
            + r"\>",
            formula,
            )

    def row_range_replace(instance):
        row_start = evaluate(cell_position, instance.group("row_start"))
        row_end = evaluate(cell_position, instance.group("row_end"))
        sel = sel_types.RowRange(
            start=sheet_types.Index(row_start),
            # make exclusive
            end=sheet_types.Bound(row_end+1),
        )
        pos = get_row_range_positions(sel)

        expr_arr = []
        for p in pos:
            r = node.add_dependency(p)
            expr = f"EVAL<{r}>"
            expr_arr.append(expr)
        compiled = "[{}]".format(",".join(expr_arr))

        return compiled

    formula = replace_instances(
        formula,
        row_range_instances,
        row_range_replace,
    )

    row_instances = re.finditer(
            r"\<R#"
            + r"(?P<row>{})".format(expression_regex)
            + r"\>",
            formula,
            )

    def row_replace(instance):
        row = evaluate(cell_position, instance.group("row"))
        sel = sel_types.RowRange(
            start=sheet_types.Index(row),
            end=sheet_types.Bound(row+1),
        )
        pos = get_row_range_positions(sel)

        expr_arr = []
        for p in pos:
            r = node.add_dependency(p)
            expr = f"EVAL<{r}>"
            expr_arr.append(expr)
        compiled = "[{}]".format(",".join(expr_arr))

        return compiled

    formula = replace_instances(
        formula,
        row_instances,
        row_replace,
    )

    # expressions should not have :
    col_range_instances = re.finditer(
            r"\<C#"
            + r"(?P<col_start>{}):".format(expression_regex)
            + r"(?P<col_end>{})".format(expression_regex)
            + r"\>",
            formula,
            )

    def col_range_replace(instance):
        col_start = evaluate(cell_position, instance.group("col_start"))
        col_end = evaluate(cell_position, instance.group("col_end"))
        sel = sel_types.ColRange(
            start=sheet_types.Index(col_start),
            # make exclusive
            end=sheet_types.Bound(col_end+1),
        )
        pos = get_col_range_positions(sel)

        expr_arr = []
        for p in pos:
            r = node.add_dependency(p)
            expr = f"EVAL<{r}>"
            expr_arr.append(expr)
        compiled = "[{}]".format(",".join(expr_arr))

        return compiled

    formula = replace_instances(
        formula,
        col_range_instances,
        col_range_replace,
    )

    col_instances = re.finditer(
            r"\<C#"
            + r"(?P<col>{})".format(expression_regex)
            + r"\>",
            formula,
            )

    def col_replace(instance):
        col = evaluate(cell_position, instance.group("col"))
        sel = sel_types.ColRange(
            start=sheet_types.Index(col),
            end=sheet_types.Bound(col+1),
        )
        pos = get_col_range_positions(sel)

        expr_arr = []
        for p in pos:
            r = node.add_dependency(p)
            expr = f"EVAL<{r}>"
            expr_arr.append(expr)
        compiled = "[{}]".format(",".join(expr_arr))

        return compiled

    formula = replace_instances(
        formula,
        col_instances,
        col_replace,
    )

    node.formula = formula
    return node


# Cast string to basic value if possible.
# If user insists on the value being a string,
# which is much more unlikely,
# they should input the value as a
# a string in a formula, e.g. ="4.0".
def cast(value):
    if value == "":
        return None

    if value == "False":
        return False
    if value == "True":
        return True

    try:
        return int(value)
    except:
        pass

    try:
        return float(value)
    except:
        pass

    return value


def dump_value(value):
    if value == None:
        return "None"
    elif value == True:
        return "True"
    elif value == False:
        return "False"
    elif isinstance(value, int):
        return f"{value}"
    elif isinstance(value, float):
        return f"{value}"
    else: # treat as string
        return f"\"{value}\""


# Compilation before DAG-evaluation.
def pre_compile(cell_position, formula):
    node = Node(formula=formula, dependencies=[])
    node = position_references(cell_position, node)
    node = selections(cell_position, node)
    return node


# Compilation after DAG-evaluation.
def post_compile(cell_position, formula):
    return formula
