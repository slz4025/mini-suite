import re
from typing import Set

import src.errors as errors
import src.sheet as sheet
import src.selection.types as sel_types

import src.computer.compiler as compiler
import src.computer.markdown as markdown


def is_formula(underlying_value):
    return isinstance(underlying_value, str) and underlying_value.startswith("=")


def is_markdown(underlying_value):
    return isinstance(underlying_value, str) and underlying_value.startswith("!")


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
        compiled_value = compiler.dump_value(value)
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


def compute_formula(cell_position, underlying_value):
    node = compiler.pre_compile(cell_position, formula)
    formula_with_evaluated_deps = evaluate_dependencies(cell_position, node)
    formula_post_compile = compiler.post_compile(cell_position, formula_with_evaluated_deps)
    value = evaluate(cell_position, formula_post_compile)
    return value


def compute_underlying_value(cell_position, underlying_value):
    if is_formula(underlying_value):
        formula = underlying_value.removeprefix("=")
        value = compute_formula(cell_position, formula)
    elif is_markdown(underlying_value):
        md = underlying_value.removeprefix("!")
        value = markdown.convert_to_html(md)
    else:
        value = underlying_value
    return value


# This function should not be called on the same
# position more than once within a call-stack.
# If it is, this indicates a dependency loop.
visited: Set[sel_types.CellPosition] = set()


# This function will begin a tree of computation like so:
# try_compute -> compute_underlying_value -> compute_formula -> evaluate_dependencies -> try_compute(dep)
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

    underlying_value = sheet.get_cell_value(cell_position)

    visited.add(cell_position)
    value = compute_underlying_value(cell_position, underlying_value)
    visited.remove(cell_position)

    return value


def compute(cell_position):
    # reset call stack
    global visited
    visited = set()

    return try_compute(cell_position)
