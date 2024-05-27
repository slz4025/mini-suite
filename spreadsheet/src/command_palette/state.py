
def get_show(session):
    show = session["show-command-palette"] == 'True'
    return show


def set_show(session, show):
    session["show-command-palette"] = str(show)


def get_show_help(session):
    show_help = session["show-help"] == 'True'
    return show_help


def set_show_help(session, show_help):
    session["show-help"] = str(show_help)


def get_show_editor(session):
    show_editor = session["show-editor"] == 'True'
    return show_editor


def set_show_editor(session, show_editor):
    session["show-editor"] = str(show_editor)


def get_show_selector(session):
    show_selector = session["show-selector"] == 'True'
    return show_selector


def set_show_selector(session, show_selector):
    session["show-selector"] = str(show_selector)


def get_show_bulk_editor(session):
    show_bulk_editor = session["show-bulk-editor"] == 'True'
    return show_bulk_editor


def set_show_bulk_editor(session, show_bulk_editor):
    session["show-bulk-editor"] = str(show_bulk_editor)


def get_show_viewer(session):
    show_viewer = session["show-viewer"] == 'True'
    return show_viewer


def set_show_viewer(session, show_viewer):
    session["show-viewer"] = str(show_viewer)
