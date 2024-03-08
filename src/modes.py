from dataclasses import dataclass
from typing import Callable

import src.errors as errors


@dataclass
class Mode:
    name: str
    check_on: Callable[[object], bool]
    set: Callable[[object, bool], None]


def check_help(session):
    return session["help-state"] == "True"


def set_help(session, state):
    session["help-state"] = str(state)


def check_editor(session):
    return session["editor-state"] == "True"


def set_editor(session, state):
    session["editor-state"] = str(state)


def check_selection(session):
    return session["selection-state"] == "True"


def set_selection(session, state):
    session["selection-state"] = str(state)


def check_bulk_editor(session):
    return session["bulk-editor-state"] == "True"


def set_bulk_editor(session, state):
    session["bulk-editor-state"] = str(state)


def check_navigator(session):
    return session["navigator-state"] == "True"


def set_navigator(session, state):
    session["navigator-state"] = str(state)


def check_settings(session):
    return session["settings-state"] == "True"


def set_settings(session, state):
    session["settings-state"] = str(state)


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
        "Selection": Mode(
            name="Selection",
            check_on=check_selection,
            set=set_selection,
        ),
        "Bulk-Editor": Mode(
            name="Bulk-Editor",
            check_on=check_bulk_editor,
            set=set_bulk_editor,
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
        raise errors.UnknownOptionError(f"'{name}' is not a valid mode.")
    mode = modes[name]
    return mode


def check(session, name):
    mode = get_mode(name)
    return mode.check_on(session)


def set(session, name, state):
    mode = get_mode(name)
    mode.set(session, state)


def init(session):
    for m, mode in modes.items():
        mode.set(session, False)


def get_str(session):
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
