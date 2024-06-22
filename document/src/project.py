from flask import render_template, Response, send_from_directory

import os

from settings import Settings
import src.block as block


FILE_PATH = None


def setup(path):
    global FILE_PATH
    FILE_PATH = path


def get_dir():
    dir, basename = os.path.split(FILE_PATH)
    return dir


def get_name():
    dir, basename = os.path.split(FILE_PATH)
    return basename


def render_null():
    return render_template(
            "partials/null.html",
            )


def render_banner(show_saved=False):
    return render_template(
            "partials/banner.html",
            show_saved=show_saved,
            )


def render_body():
    null = render_null()
    banner_html = render_banner(show_saved=False)
    blocks_html = block.render_all(
            base_rel_path=get_dir(),
            )
    return render_template(
            "partials/body.html",
            banner=banner_html,
            null=null,
            name=get_name(),
            blocks=blocks_html,
            )


def render():
    dark_mode = Settings.DARK_MODE
    body = render_body()
    return render_template(
            "index.html",
            tab_name=get_name(),
            dark_mode=dark_mode,
            body=body,
            )


def root():
    contents = ""
    if os.path.isfile(FILE_PATH):
        with open(FILE_PATH, 'r') as file:
            contents = file.read()
    block.set_all_markdown(contents)
    return render()


def block_render(id):
    return block.render(id=id, base_rel_path=get_dir())


def block_focus(id):
    prev_in_focus = block.get_in_focus()
    block.set_in_focus(id)

    html = block.render(id, base_rel_path=get_dir())
    resp = Response(html)
    if prev_in_focus is not None:
        # rerender so shows as unfocused
        resp.headers['HX-Trigger'] = f"block-{prev_in_focus}"
    return resp


def block_unfocus():
    id = block.get_in_focus()
    block.reset_in_focus()

    return block.render(id, base_rel_path=get_dir())


def block_next():
    id = block.get_in_focus()
    block.set_next_in_focus()

    html = block.render(id, base_rel_path=get_dir())
    resp = Response(html)
    next_in_focus = block.get_in_focus()
    if next_in_focus != id:
        resp.headers['HX-Trigger'] = f"block-{next_in_focus}"
    return resp


def block_prev():
    id = block.get_in_focus()
    block.set_prev_in_focus()

    html = block.render(id, base_rel_path=get_dir())
    resp = Response(html)
    next_in_focus = block.get_in_focus()
    if next_in_focus != id:
        resp.headers['HX-Trigger'] = f"block-{next_in_focus}"
    return resp


def block_edit(contents):
    id = block.get_in_focus()
    block.set_markdown(contents, id=id)

    return render_null()


def block_insert():
    id = block.get_in_focus()

    return block.insert(id, base_rel_path=get_dir())


def block_delete():
    id = block.get_in_focus()

    return block.delete(id)


def get_file_obj(filepath):
    filepath = "/" + filepath
    filedir, filename = os.path.split(filepath)
    return send_from_directory(filedir, filename)


def save():
    markdown = block.get_all_markdown()
    with open(FILE_PATH, 'w+') as file:
        file.write(markdown)

    html = render_banner(show_saved=True)
    resp = Response(html)
    return resp
