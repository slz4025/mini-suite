show = None
show_help = None
show_editor = None
show_selector = None
show_bulk_editor = None
show_viewer = None


def get_show():
    return show


def set_show(_show):
    global show
    show = _show


def get_show_help():
    return show_help


def set_show_help(_show_help):
    global show_help
    show_help = _show_help


def get_show_editor():
    return show_editor


def set_show_editor(_show_editor):
    global show_editor
    show_editor = _show_editor


def get_show_selector():
    return show_selector


def set_show_selector(_show_selector):
    global show_selector
    show_selector = _show_selector


def get_show_bulk_editor():
    return show_bulk_editor


def set_show_bulk_editor(_show_bulk_editor):
    global show_bulk_editor
    show_bulk_editor = _show_bulk_editor


def get_show_viewer():
    return show_viewer


def set_show_viewer(_show_viewer):
    global show_viewer
    show_viewer = _show_viewer


def init():
    set_show(False)
    set_show_help(False)
    set_show_editor(False)
    set_show_selector(False)
    set_show_bulk_editor(False)
    set_show_viewer(False)
