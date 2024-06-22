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


def render():
    dark_mode = Settings.DARK_MODE
    null = render_null()
    banner_html = render_banner(show_saved=False)
    blocks_html = block.render_all(
            base_rel_path=get_dir(),
            )
    body_html = render_template(
            "partials/body.html",
            banner=banner_html,
            null=null,
            name=get_name(),
            blocks=blocks_html,
            )
    return render_template(
            "index.html",
            tab_name=get_name(),
            dark_mode=dark_mode,
            body=body_html,
            )


def root():
    resp = Response()

    contents = ""
    if os.path.isfile(FILE_PATH):
        with open(FILE_PATH, 'r') as file:
            contents = file.read()
    block.set_all_markdown(contents)

    html = render()
    resp.set_data(html)
    return resp


def block_render(id):
    resp = Response()

    block_html = block.render(id=id, base_rel_path=get_dir())
    resp.set_data(block_html)
    return resp


def block_focus(id):
    resp = Response()

    prev_in_focus = block.get_in_focus()
    block.set_in_focus(id)

    if prev_in_focus is not None:
        # rerender so shows as unfocused
        resp.headers['HX-Trigger'] = f"block-{prev_in_focus}"

    block_html = block.render(id, base_rel_path=get_dir())
    resp.set_data(block_html)
    return resp


def block_unfocus():
    resp = Response()

    id = block.get_in_focus()
    block.reset_in_focus()

    block_html = block.render(id, base_rel_path=get_dir())
    resp.set_data(block_html)
    return resp


def block_next():
    resp = Response()

    id = block.get_in_focus()
    block.set_next_in_focus()

    next_in_focus = block.get_in_focus()
    if next_in_focus != id:
        resp.headers['HX-Trigger'] = f"block-{next_in_focus}"

    block_html = block.render(id, base_rel_path=get_dir())
    resp.set_data(block_html)
    return resp


def block_prev():
    resp = Response()

    id = block.get_in_focus()
    block.set_prev_in_focus()

    next_in_focus = block.get_in_focus()
    if next_in_focus != id:
        resp.headers['HX-Trigger'] = f"block-{next_in_focus}"

    block_html = block.render(id, base_rel_path=get_dir())
    resp.set_data(block_html)
    return resp


def block_edit(contents):
    resp = Response()

    id = block.get_in_focus()
    block.set_markdown(contents, id=id)

    null_html = render_null()
    resp.set_data(null_html)
    return resp


def block_insert():
    resp = Response()
    id = block.get_in_focus()

    blocks_html = block.insert(id, base_rel_path=get_dir())
    resp.set_data(blocks_html)
    return blocks_html


def block_delete():
    resp = Response()
    id = block.get_in_focus()

    blocks_html = block.delete(id)
    resp.set_data(blocks_html)
    return blocks_html


def get_file_obj(filepath):
    filepath = "/" + filepath
    filedir, filename = os.path.split(filepath)
    return send_from_directory(filedir, filename)


def save():
    resp = Response()

    markdown = block.get_all_markdown()
    with open(FILE_PATH, 'w+') as file:
        file.write(markdown)

    banner_html = render_banner(show_saved=True)
    resp.set_data(banner_html)
    return resp


def reset_banner():
    resp = Response()

    banner_html = render_banner(show_saved=False)
    resp.set_data(banner_html)
    return resp
