from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin
import os
import re

# ensure circular import
import src.state as state


md = (
        MarkdownIt('commonmark', {'breaks': True, 'html': True})
        .enable('table')
        .use(anchors_plugin)
        )


def get_abs_path(path, base_path):
    path = os.path.expanduser(path)
    if not os.path.isabs(path):
        path = os.path.join(base_path, path)
        path = os.path.realpath(path)
    return path


def use_abs_media(markdown, base_path):
    media_instances = re.finditer(
            r"\!\[(?P<alt>.*)\]\((?P<path>.*)\)",
            markdown,
            )
    offset = 0
    for instance in media_instances:
        alt = instance.group("alt")
        path = instance.group("path")
        abs_path = get_abs_path(path, base_path)
        fixed = f"![{alt}]({abs_path})"

        start_index = instance.start(0) + offset
        end_index = instance.end(0) + offset
        markdown = markdown[:start_index] + fixed + markdown[end_index:]

        fixed_len = len(fixed)
        orig_len = end_index - start_index
        offset += fixed_len - orig_len

    return markdown


def use_abs_rel_links(markdown, base_path):
    link_instances = re.finditer(
            r"\[(?P<alt>.*)\]\((?P<path>.*)\)",
            markdown,
            )
    offset = 0
    for instance in link_instances:
        alt = instance.group("alt")
        path = instance.group("path")

        # definitely skip web-links and section headers
        if path.startswith("http") or path.startswith("#"):
            continue
        if not path.endswith(".md"):
            continue

        try:  # pre-emptively create markdown document entry if not exist
            abs_path = get_abs_path(path, base_path)
            entry_id = state.get_entry_id(abs_path)
            if entry_id is None:
                entry_id = state.add_entry(abs_path)
        except Exception:
            continue

        endpoint = f"/entry/{entry_id}"
        fixed = f"[{alt}]({endpoint})"

        start_index = instance.start(0) + offset
        end_index = instance.end(0) + offset
        markdown = markdown[:start_index] + fixed + markdown[end_index:]

        fixed_len = len(fixed)
        orig_len = end_index - start_index
        offset += fixed_len - orig_len

    return markdown


def get_html(markdown, base_path):
    markdown = use_abs_media(markdown, base_path)
    markdown = use_abs_rel_links(markdown, base_path)

    html = md.render(markdown)
    return html
