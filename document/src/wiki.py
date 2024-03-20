from markdown_it import MarkdownIt
import os
import re
import shutil

import src.errors as errors


md = (
    MarkdownIt('commonmark', {'breaks': True, 'html': True})
    .enable('table')
)


DOWNLOADS_PATH = os.path.expanduser("~/Downloads")
WIKI_PATH = None
entries = []


def get():
    return WIKI_PATH


def use(path):
    global entries
    directory_entries = os.listdir(path)
    for e in directory_entries:
        if os.path.isdir(os.path.join(path, e)):
            entries.append(e)


def set(path):
    path = os.path.expanduser(path)
    if not os.path.isdir(path):
        raise errors.UserError(f"'{path}' is not a valid directory.")

    global WIKI_PATH
    WIKI_PATH = path
    use(path)


def exists(name):
    return name in entries


def add(name):
    entries.append(name)


def create(name):
    wiki_path = get()
    dir = os.path.join(wiki_path, name)
    os.makedirs(dir)

    indexpath = os.path.join(dir, "index.md")
    file = open(indexpath, 'w+')
    file.close()

    mediadir = os.path.join(dir, "media")
    os.makedirs(mediadir)

    add(name)


def render_html(markdown):
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
        fixed = f"[alt](../{name}/index.html)"

        start_index = instance.start(0) + offset
        end_index = instance.end(0) + offset
        markdown = markdown[:start_index] + fixed + markdown[end_index:]

        fixed_len = len(fixed)
        orig_len = end_index - start_index
        offset += fixed_len - orig_len

    modified_markdown = markdown
    html = md.render(modified_markdown)
    return html


def export(session, filename):
    if filename == '':
        raise errors.UserError("File name was not given.")

    wiki_path = get()

    export_dir = os.path.join(DOWNLOADS_PATH, filename)
    try:
        os.makedirs(export_dir)
    except OSError:
        raise errors.UserError(
            f"Download folder already has entry '{filename}'."
        )

    # only exports what is saved in current entry and others
    for entry in entries:
        if entry.startswith("temp-"):
            continue

        md_dir = os.path.join(wiki_path, entry)

        html_dir = os.path.join(export_dir, entry)
        os.makedirs(html_dir)

        md_indexpath = os.path.join(md_dir, "index.md")
        with open(md_indexpath, 'r') as file:
            markdown = file.read()

        html = render_html(markdown)

        html_indexpath = os.path.join(html_dir, "index.html")
        with open(html_indexpath, 'w+') as file:
            file.write(html)

        md_mediadir = os.path.join(md_dir, "media")
        html_mediadir = os.path.join(html_dir, "media")
        shutil.copytree(md_mediadir, html_mediadir)

    filepath = os.path.join(DOWNLOADS_PATH, filename)
    shutil.make_archive(filepath, 'zip', DOWNLOADS_PATH, export_dir)