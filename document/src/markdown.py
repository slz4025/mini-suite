from markdown_it import MarkdownIt
import os
import re


md = (
        MarkdownIt('commonmark', {'breaks': True, 'html': True})
        .enable('table')
        )


def use_abs_path(markdown, base_rel_path):
    media_instances = re.finditer(
            r"\!\[(?P<alt>.*)\]\((?P<path>.*)\)",
            markdown,
            )
    offset = 0
    for instance in media_instances:
        alt = instance.group("alt")
        path = instance.group("path")
        abs_path = os.path.join(base_rel_path, path)
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
        abs_path = os.path.join(base_rel_path, path)
        fixed = f"[{alt}]({abs_path})"

        start_index = instance.start(0) + offset
        end_index = instance.end(0) + offset
        markdown = markdown[:start_index] + fixed + markdown[end_index:]

        fixed_len = len(fixed)
        orig_len = end_index - start_index
        offset += fixed_len - orig_len

    return markdown


def use_rel_wiki_path(markdown):
    media_instances = re.finditer(
            r"\!\[(?P<alt>.*)\]\(\/media\/(?P<media_id>.*)\)",
            markdown,
            )
    offset = 0
    for instance in media_instances:
        alt = instance.group("alt")
        media_id = instance.group("media_id")
        fixed = f"![{alt}](./media/{media_id})"

        start_index = instance.start(0) + offset
        end_index = instance.end(0) + offset
        markdown = markdown[:start_index] + fixed + markdown[end_index:]

        fixed_len = len(fixed)
        orig_len = end_index - start_index
        offset += fixed_len - orig_len

    link_instances = re.finditer(
            r"\[(?P<alt>.*)\]\(\/entry\/(?P<name>.*)\)",
            markdown,
            )
    offset = 0
    for instance in link_instances:
        alt = instance.group("alt")
        name = instance.group("name")
        fixed = f"[{alt}](../{name}/index.html)"

        start_index = instance.start(0) + offset
        end_index = instance.end(0) + offset
        markdown = markdown[:start_index] + fixed + markdown[end_index:]

        fixed_len = len(fixed)
        orig_len = end_index - start_index
        offset += fixed_len - orig_len

    return markdown


def html_for_internal(markdown, base_rel_path):
    if base_rel_path is not None:
        markdown = use_abs_path(markdown, base_rel_path)

    html = md.render(markdown)
    return html


def html_for_external(markdown):
    markdown = use_rel_wiki_path(markdown)

    html = md.render(markdown)
    return html
