
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


def get_show_selection(session):
    show_selection = session["show-selection"] == 'True'
    return show_selection


def set_show_selection(session, show_selection):
    session["show-selection"] = str(show_selection)


def get_show_bulk_editor(session):
    show_bulk_editor = session["show-bulk-editor"] == 'True'
    return show_bulk_editor


def set_show_bulk_editor(session, show_bulk_editor):
    session["show-bulk-editor"] = str(show_bulk_editor)


def get_show_port_viewer(session):
    show_port_viewer = session["show-port-viewer"] == 'True'
    return show_port_viewer


def set_show_port_viewer(session, show_port_viewer):
    session["show-port-viewer"] = str(show_port_viewer)
