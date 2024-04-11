import re
from typing import Set

import src.errors as errors
import src.sheet as sheet
import src.selection.types as sel_types

import src.computer.compiler as compiler


def is_formula(formula):
    return isinstance(formula, str) and formula.startswith("=")


# Cast value to string if not basic type.
# If user insists on the value being a string,
# which is much more unlikely,
# they should input the value as a
# a string in a formula, e.g. ="4.0".
def cast(value):
    if isinstance(value, bool):
        return value
    elif isinstance(value, int):
        return value
    elif isinstance(value, float):
        return value
    else:
        return f"\"{value}\""


def evaluate_dependencies(cell_position, node):
    formula = node.formula

    eval_instances = re.finditer(
            r"EVAL\<"
            + r"(?P<register>[0-9]+)"
            + r"\>",
            formula,
            )

    def eval_replace(instance):
        register = int(instance.group("register"))
        pos = node.get_dependency(register)
        value = try_compute(pos)
        # Put value in string to put in formula.
        compiled_value = str(cast(value))
        return compiled_value

    formula = compiler.replace_instances(
        formula,
        eval_instances,
        eval_replace,
    )
    return formula


def evaluate(cell_position, formula):
    try:
        value = eval(formula)
    except Exception as e:
        raise errors.UserError(
            "Evaluation of compiled formula at cell position "
            f"({cell_position.row_index.value}, "
            f"{cell_position.col_index.value}) "
            f"encountered error: {e}.\n"
            f"Compiled formula: {formula}"
        )
    return value


def compute_formula(cell_position, formula):
    if not is_formula(formula):
        value = formula
    else:
        formula = formula.removeprefix("=")
        node = compiler.pre_compile(cell_position, formula)
        formula = evaluate_dependencies(cell_position, node)
        formula = compiler.post_compile(cell_position, formula)
        value = evaluate(cell_position, formula)
    return value


# This function should not be called on the same
# position more than once within a call-stack.
# If it is, this indicates a dependency loop.
visited: Set[sel_types.CellPosition] = set()


def try_compute(cell_position):
    global visited

    if cell_position in visited:
        raise errors.UserError(
            "Dependency loop in computing cell values. "
            "Cell at position ("
            f"{cell_position.row_index.value},"
            f"{cell_position.col_index.value}"
            ") visited more than once."
        )

    formula = sheet.get_cell_value(cell_position)

    visited.add(cell_position)
    value = compute_formula(cell_position, formula)
    visited.remove(cell_position)

    return value


def compute(cell_position):
    # reset call stack
    global visited
    visited = set()

    return try_compute(cell_position)
