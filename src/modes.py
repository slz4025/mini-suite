from dataclasses import dataclass
from typing import Callable


@dataclass
class Mode:
    name: str
    check_on: Callable[[object], bool]
    set: Callable[[object, bool], None]


def check_help(session):
    return session["help"] == "True"


def set_help(session, state):
    session["help"] = str(state)


def check_editor(session):
    return session["editor"] == "True"


def set_editor(session, state):
    session["editor"] = str(state)


def check_bulk_edit(session):
    return session["bulk-edit"] == "True"


def set_bulk_edit(session, state):
    session["bulk-edit"] = str(state)


def check_navigator(session):
    return session["navigator"] == "True"


def set_navigator(session, state):
    session["navigator"] = str(state)


def check_settings(session):
    return session["settings"] == "True"


def set_settings(session, state):
    session["settings"] = str(state)


modes = {
        "Help": Mode(
            name="Help",
            check_on=check_help,
            set=set_help,
        ),
        "Editor": Mode(
            name="Editor",
            check_on=check_editor,
            set=set_editor,
        ),
        "Bulk-Edit": Mode(
            name="Bulk-Edit",
            check_on=check_bulk_edit,
            set=set_bulk_edit,
        ),
        "Navigator": Mode(
            name="Navigator",
            check_on=check_navigator,
            set=set_navigator,
        ),
        "Settings": Mode(
            name="Settings",
            check_on=check_settings,
            set=set_settings,
        ),
}


def get_mode(name):
    if name not in modes:
        raise Exception(f"'{name}' is not a valid mode.")
    mode = modes[name]
    return mode


def check_mode(session, name):
    mode = get_mode(name)
    return mode.check_on(session)


def set_mode(session, name, state):
    mode = get_mode(name)
    mode.set(session, state)


def init_modes(session):
    for m, mode in modes.items():
        mode.set(session, False)


def get_modes_str(session):
    inner = ""
    first = True
    for m, mode in modes.items():
        if mode.check_on(session):
            if first:
                inner += mode.name
                first = False
            else:
                inner += ", " + mode.name

    modes_str = ""
    if not first:
        modes_str += f"({inner})"
    modes_str += " >"
    return modes_str
