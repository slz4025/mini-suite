from markdown_it import MarkdownIt
import re


md = (
        MarkdownIt('commonmark', {'breaks': True, 'html': True})
        .enable('table')
        )


def html_for_internal(markdown):
    html = md.render(markdown)
    return html


def html_for_external(markdown):
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

    html = md.render(markdown)
    return html
