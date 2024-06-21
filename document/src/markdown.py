from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin
import os
import re


md = (
        MarkdownIt('commonmark', {'breaks': True, 'html': True})
        .enable('table')
        .use(anchors_plugin)
        )


def get_abs_path(path, base_rel_path):
    path = os.path.expanduser(path)
    if not os.path.isabs(path):
        path = os.path.join(base_rel_path, path)
    return path


def use_abs_path(markdown, base_rel_path):
    media_instances = re.finditer(
            r"\!\[(?P<alt>.*)\]\((?P<path>.*)\)",
            markdown,
            )
    offset = 0
    for instance in media_instances:
        alt = instance.group("alt")
        path = instance.group("path")
        abs_path = get_abs_path(path, base_rel_path)
        fixed = f"![{alt}]({abs_path})"

        start_index = instance.start(0) + offset
        end_index = instance.end(0) + offset
        markdown = markdown[:start_index] + fixed + markdown[end_index:]

        fixed_len = len(fixed)
        orig_len = end_index - start_index
        offset += fixed_len - orig_len

    link_instances = re.finditer(
            r"\[(?P<alt>.*)\]\((?P<path>.*)\)",
            markdown,
            )
    offset = 0
    for instance in link_instances:
        alt = instance.group("alt")
        path = instance.group("path")

        # skip web-links and section headers
        if path.startswith("http") or path.startswith("#"):
            continue

        abs_path = get_abs_path(path, base_rel_path)
        fixed = f"[{alt}]({abs_path})"

        start_index = instance.start(0) + offset
        end_index = instance.end(0) + offset
        markdown = markdown[:start_index] + fixed + markdown[end_index:]

        fixed_len = len(fixed)
        orig_len = end_index - start_index
        offset += fixed_len - orig_len

    return markdown


def get_html(markdown, base_rel_path):
    if base_rel_path is not None:
        markdown = use_abs_path(markdown, base_rel_path)

    html = md.render(markdown)
    return html
