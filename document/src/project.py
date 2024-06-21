from flask import render_template, Response, send_from_directory

import os

from settings import Settings
import src.block as block
import src.command_palette as command_palette
import src.notifications as notifications


FILE_PATH = None


def setup(path):
    global FILE_PATH
    FILE_PATH = path

    command_palette.init(show=False)
    notifications.init()


def get_dir():
    dir, basename = os.path.split(FILE_PATH)
    return dir


def get_name():
    dir, basename = os.path.split(FILE_PATH)
    return basename


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
            )

    blocks_html = block.render_all(
            session,
            base_rel_path=get_dir(),
            )
    return render_template(
            "partials/body.html",
            dark_mode=dark_mode,
            show_command_palette=show_command_palette,
            null=null,
            notification_banner=notification_banner_html,
            command_palette=command_palette_html,
            current_entry=get_name(),
            blocks=blocks_html,
            )


def render(session):
    body = render_body(session)
    return render_template(
            "index.html",
            body=body,
            tab_name=get_name(),
            )


def root(session):
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


def command_palette_toggle(session, state):
    show = state == 'open'
    command_palette.set_show(show)

    return render_body(session)


def block_unfocus(session):
    id = block.get_in_focus(session)
    block.reset_in_focus(session)

    return block.render(
            session,
            id,
            base_rel_path=get_dir(),
            )


def block_focus(session, id):
    prev_in_focus = block.get_in_focus(session)
    block.set_in_focus(session, id)

    html = block.render(
            session,
            id,
            base_rel_path=get_dir(),
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
            base_rel_path=get_dir(),
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
            base_rel_path=get_dir(),
            )
    resp = Response(html)
    next_in_focus = block.get_in_focus(session)
    if next_in_focus != id:
        resp.headers['HX-Trigger'] = f"block-{next_in_focus}"
    return resp


def block_edit(session, id, contents):
    block.set_markdown(contents, id=id)

    return render_null(session)


def get_file_obj(session, filepath):
    filepath = "/" + filepath
    filedir, filename = os.path.split(filepath)
    return send_from_directory(filedir, filename)


def block_insert(session, id):
    return block.insert(
            session,
            id,
            base_rel_path=get_dir(),
            )


def block_delete(session, id):
    return block.delete(session, id)


def block_render(session, id):
    return block.render(
            session,
            id=id,
            base_rel_path=get_dir(),
            )


def save_entry(session):
    markdown = block.get_all_markdown(session)
    with open(FILE_PATH, 'w+') as file:
        file.write(markdown)

    html = render_null(session)
    resp = Response(html)
    notifications.set_info("Entry saved.")
    resp.headers['HX-Trigger'] = "notification"
    return resp
