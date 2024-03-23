from flask import render_template

import src.bulk_editor as bulk_editor
import src.editor as editor
import src.files as files
import src.navigator as navigator
import src.selection as selection
import src.settings as settings


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


def get_show_navigator(session):
    show_navigator = session["show-navigator"] == 'True'
    return show_navigator


def set_show_navigator(session, show_navigator):
    session["show-navigator"] = str(show_navigator)


def get_show_files(session):
    show_files = session["show-files"] == 'True'
    return show_files


def set_show_files(session, show_files):
    session["show-files"] = str(show_files)


def get_show_settings(session):
    show_settings = session["show-settings"] == 'True'
    return show_settings


def set_show_settings(session, show_settings):
    session["show-settings"] = str(show_settings)


def render(session):
    show_command_palette = get_show(session)
    show_help = get_show_help(session)

    editor_html = editor.render(session)
    selection_html = selection.render(session)
    bulk_editor_html = bulk_editor.render(session)
    navigator_html = navigator.render(session)
    files_html = files.render(session)
    settings_html = settings.render(session)

    command_palette = render_template(
            "partials/command_palette.html",
            show_command_palette=show_command_palette,
            show_help=show_help,
            editor=editor_html,
            selection=selection_html,
            bulk_editor=bulk_editor_html,
            navigator=navigator_html,
            files=files_html,
            settings=settings_html,
    )
    return command_palette


def init(session):
    show = True
    set_show(session, show)

    show_help = False
    set_show_help(session, show_help)
    show_editor = False
    set_show_editor(session, show_editor)
    show_selection = False
    set_show_selection(session, show_selection)
    show_bulk_editor = False
    set_show_bulk_editor(session, show_bulk_editor)
    show_navigator = False
    set_show_navigator(session, show_navigator)
    show_files = False
    set_show_files(session, show_files)
    show_settings = False
    set_show_settings(session, show_settings)
