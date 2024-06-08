from enum import Enum
from flask import render_template, Response, redirect, send_from_directory

import os

from settings import Settings
import src.block as block
import src.command_palette as command_palette
import src.entry as entry
import src.errors as errors
import src.notifications as notifications
import src.selector as selector
import src.wiki as wiki


class Mode(Enum):
    FILE = 1
    WIKI = 2


MODE = None
FILE_PATH = None
FILE_DIR = None
FILE_NAME = None
TAB_NAME = None


def setup(wiki_path, one_off_file):
    global TAB_NAME, MODE

    if one_off_file is not None:
        global FILE_PATH, FILE_DIR, FILE_NAME
        dir, basename = os.path.split(one_off_file)
        FILE_NAME = basename
        FILE_DIR = dir
        FILE_PATH = one_off_file
        MODE = Mode.FILE
        TAB_NAME = FILE_NAME
        command_palette.init(show=False)
    elif wiki_path is not None:
        wiki.set(wiki_path)
        MODE = Mode.WIKI
        _, basename = os.path.split(wiki_path)
        TAB_NAME = basename
        command_palette.init(show=True)
    else:
        raise Exception("Mode not specified.")

    notifications.init()


def check_using_file():
    if MODE != Mode.FILE:
        raise Exception("Not in one-off file mode.")


def check_using_wiki():
    if MODE != Mode.WIKI:
        raise Exception("Not in wiki mode.")


def check_in_wiki(name):
    entry.check_name(name)
    wiki.check_exists(name)


def render_null(session):
    return render_template(
            "partials/null.html",
            )


def render_body(session):
    dark_mode = Settings.DARK_MODE
    null = render_null(session)
    notification_banner_html = notifications.render(session)
    show_command_palette = command_palette.get_show()
    command_palette_html = command_palette.render(
            session,
            show_io=MODE == Mode.WIKI,
            )

    match MODE:
        case Mode.FILE:
            current_entry = FILE_NAME
        case Mode.WIKI:
            current_entry = entry.get_name()

    blocks_html = block.render_all(
            session,
            show_linking=MODE == Mode.WIKI,
            base_rel_path=FILE_DIR,
            )
    return render_template(
            "partials/body.html",
            dark_mode=dark_mode,
            show_command_palette=show_command_palette,
            null=null,
            notification_banner=notification_banner_html,
            command_palette=command_palette_html,
            non_editable_title=MODE == Mode.FILE,
            current_entry=current_entry if current_entry is not None else '',
            blocks=blocks_html,
            )


def render(session):
    body = render_body(session)
    return render_template(
            "index.html",
            body=body,
            tab_name=TAB_NAME,
            )


def get_file(files):
    if 'input' not in files:
        raise errors.UserError("File was not chosen.")
    file = files['input']
    return file


def root(session):
    match MODE:
        case Mode.FILE:
            return redirect("/file")
        case Mode.WIKI:
            return redirect("/entry/temp")


def get_one_off_file(session):
    check_using_file()

    contents = ""
    if os.path.isfile(FILE_PATH):
        with open(FILE_PATH, 'r') as file:
            contents = file.read()
    block.set_all_markdown(session, contents)

    return render(session)


def notification(session, show):
    show_notifications = show == "on"
    if not show_notifications:
        notifications.reset()

    return notifications.render(session)


def command_palette_operation(session, operation):
    check_using_wiki()

    return command_palette.render_operation(session, operation)


def command_palette_toggle(session, state):
    show = state == 'open'
    command_palette.set_show(show)

    return render_body(session)


def get_block_in_focus(session):
    return block.get_in_focus(session)


def block_operation(session, id, operation):
    return block.render_operation(session, id, operation)


def block_unfocus(session):
    id = block.get_in_focus(session)
    block.reset_in_focus(session)

    return block.render(
            session,
            id,
            show_linking=MODE == Mode.WIKI,
            base_rel_path=FILE_DIR,
            )


def block_focus(session, id):
    prev_in_focus = block.get_in_focus(session)
    block.set_in_focus(session, id)

    html = block.render(
            session,
            id,
            show_linking=MODE == Mode.WIKI,
            base_rel_path=FILE_DIR,
            )
    resp = Response(html)
    if prev_in_focus is not None:
        # rerender so shows as unfocused
        resp.headers['HX-Trigger'] = f"block-{prev_in_focus}"
    return resp


def block_next(session):
    id = block.get_in_focus(session)
    block.set_next_in_focus(session)

    html = block.render(
            session,
            id,
            show_linking=MODE == Mode.WIKI,
            base_rel_path=FILE_DIR,
            )
    resp = Response(html)
    next_in_focus = block.get_in_focus(session)
    if next_in_focus != id:
        resp.headers['HX-Trigger'] = f"block-{next_in_focus}"
    return resp


def block_prev(session):
    id = block.get_in_focus(session)
    block.set_prev_in_focus(session)

    html = block.render(
            session,
            id,
            show_linking=MODE == Mode.WIKI,
            base_rel_path=FILE_DIR,
            )
    resp = Response(html)
    next_in_focus = block.get_in_focus(session)
    if next_in_focus != id:
        resp.headers['HX-Trigger'] = f"block-{next_in_focus}"
    return resp


def block_edit(session, id, contents):
    block.set_markdown(contents, id=id)

    return render_null(session)


def block_link(session, id, name):
    check_using_wiki()

    error = None
    try:
        check_in_wiki(name)
        block.add_link(session, id, name)
    except errors.UserError as e:
        error = e

    if error is not None:
        notifications.set_error(error)
    else:
        notifications.set_info("Link added.")

    html = block.render(
            session,
            id,
            show_linking=MODE == Mode.WIKI,
            base_rel_path=FILE_DIR,
            )
    resp = Response(html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


def get_file_obj(session, filepath):
    check_using_file()

    filepath = "/" + filepath
    filedir, filename = os.path.split(filepath)
    return send_from_directory(filedir, filename)


def get_media(session, filename):
    check_using_wiki()

    return entry.get_media(session, filename)


def block_media(request, session, id):
    check_using_wiki()

    error = None
    try:
        file = get_file(request.files)
        media_id = entry.save_media(session, file)
        block.append_media_reference(session, id, media_id, alt=file.name)
    except errors.UserError as e:
        error = e

    if error is not None:
        notifications.set_error(error)
    else:
        notifications.set_info("Media appended.")

    html = block.render(
            session,
            id,
            show_linking=MODE == Mode.WIKI,
            base_rel_path=FILE_DIR,
            )
    resp = Response(html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


def block_insert(session, id):
    return block.insert(
            session,
            id,
            show_linking=MODE == Mode.WIKI,
            base_rel_path=FILE_DIR,
            )


def block_delete(session, id):
    return block.delete(session, id)


def block_render(session, id):
    return block.render(
            session,
            id=id,
            show_linking=MODE == Mode.WIKI,
            base_rel_path=FILE_DIR,
            )


def new_entry(session):
    check_using_wiki()

    notifications.set_info("Creating new entry.")
    resp = Response()
    resp.headers["HX-Redirect"] = "/entry/temp"
    return resp


def open_entry(session, name):
    check_using_wiki()

    error = None
    try:
        check_in_wiki(name)
    except errors.UserError as e:
        error = e

    if error is not None:
        notifications.set_error(error)
        html = render_null(session)
        resp = Response(html)
        resp.headers['HX-Trigger'] = "notification"
        return resp
    else:
        resp = Response()
        notifications.set_info("Entry opened.")
        resp.headers["HX-Redirect"] = f"/entry/{name}"
        return resp


def save_entry(session, name):
    match MODE:
        case Mode.FILE:
            if name != FILE_NAME:
                raise Exception("Cannot change name in one-file mode.")

            markdown = block.get_all_markdown(session)
            with open(FILE_PATH, 'w+') as file:
                file.write(markdown)

            html = render_null(session)
            resp = Response(html)
            notifications.set_info("Entry saved.")
            resp.headers['HX-Trigger'] = "notification"
            return resp

        case Mode.WIKI:
            error = None
            try:
                entry.save(session, name)
            except errors.UserError as e:
                error = e

            if error is not None:
                notifications.set_error(error)
                html = render_null(session)
                resp = Response(html)
                resp.headers['HX-Trigger'] = "notification"
                return resp
            else:
                resp = Response()
                notifications.set_info("Entry saved.")
                resp.headers["HX-Redirect"] = f"/entry/{name}"
                return resp


def get_entry_results(session, operation, search):
    check_using_wiki()

    return selector.render_results(session, operation, search)


def get_temp_entry(session):
    check_using_wiki()

    entry.use_temp(session)

    return render(session)


def get_wiki_entry(session, name):
    check_using_wiki()

    error = None
    try:
        entry.set(session, name)
    except errors.UserError as e:
        error = e

    if error is not None:
        notifications.set_error(error)
        return redirect("/")
    else:
        return render(session)


def import_markdown(request, session):
    check_using_wiki()

    error = None
    try:
        file = get_file(request.files)
        entry.import_file(session, file)
    except errors.UserError as e:
        error = e

    if error is not None:
        notifications.set_error(error)
    else:
        notifications.set_info("Markdown imported.")

    html = block.render_all(session)
    resp = Response(html)
    resp.headers['HX-Trigger'] = "notification"
    return resp


def export_html(session, filename):
    check_using_wiki()

    error = None
    try:
        entry.export(session, filename)
    except errors.UserError as e:
        error = e

    if error is not None:
        notifications.set_error(error)
    else:
        notifications.set_info("HTML exported.")

    html = render_null(session)
    resp = Response(html)
    resp.headers['HX-Trigger'] = "notification"
    return resp
