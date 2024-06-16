from src.bulk_editor.operations.cut import Cut
from src.bulk_editor.operations.copy import Copy
from src.bulk_editor.operations.paste import Paste
from src.bulk_editor.operations.delete import Delete
from src.bulk_editor.operations.insert import Insert
from src.bulk_editor.operations.move import Move
from src.bulk_editor.operations.sort import Sort
from src.bulk_editor.operations.reverse import Reverse
from src.bulk_editor.operations.erase import Erase
from src.bulk_editor.operations.value import Value


operations = [
    Cut,
    Copy,
    Paste,
    Delete,
    Insert,
    Move,
    Sort,
    Reverse,
    Erase,
    Value,
]
operations_map = {o.name(): o for o in operations}


def get_options():
    return operations_map.keys()


def get(name):
    return operations_map[name]


def validate_and_parse(name, form):
    operation = get(name)
    mods = operation.validate_and_parse(form)
    return mods


def apply(name, mods):
    operation = get(name)
    operation.apply(mods)


def render(name):
    operation = get(name)
    return operation.render()
