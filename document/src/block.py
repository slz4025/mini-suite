from flask import render_template
from typing import Dict, List
import uuid

import src.markdown as md


all_markdown: Dict[str, str] = {}


in_focus = None


def get_in_focus():
    return in_focus


def set_in_focus(id):
    global in_focus
    in_focus = id


def reset_in_focus():
    global in_focus
    in_focus = None


def get_markdown(id):
    global all_markdown
    if id not in all_markdown:
        raise Exception(f"'{id}' is not associated with markdown.")
    return all_markdown[id]


def set_markdown(markdown, id):
    global all_markdown
    all_markdown[id] = markdown


def remove_markdown(id):
    global all_markdown
    del all_markdown[id]


order: List[str]
reverse_order: Dict[str, int]


def get_id(pos):
    if pos < 0 or pos >= len(order):
        raise Exception(f"Position {pos} is not valid.")
    return order[pos]


def get_pos(id):
    if id not in reverse_order:
        raise Exception("Id 'id' does not have valid block position.")
    return reverse_order[id]


def remove_from_order(id):
    global order, reverse_order

    pos = get_pos(id)
    order = order[:pos] + order[pos+1:]

    del reverse_order[id]
    # shift-right everything after
    for i in range(pos, len(order)):
        temp_id = order[i]
        assert i == reverse_order[temp_id] - 1
        reverse_order[temp_id] = i


def insert_into_order(id, pos):
    global order, reverse_order

    order = order[:pos] + [id] + order[pos:]
    reverse_order[id] = pos

    # shift-right everything after
    for i in range(pos+1, len(order)):
        temp_id = order[i]
        assert i == reverse_order[temp_id] + 1
        reverse_order[temp_id] = i


def create_id():
    id = uuid.uuid4().hex
    return id


def set_prev_in_focus():
    global in_focus
    pos = get_pos(in_focus)
    if pos == 0:
        return

    prev_pos = pos - 1
    prev_id = get_id(prev_pos)

    in_focus = prev_id


def set_next_in_focus():
    global in_focus
    pos = get_pos(in_focus)
    if pos == len(order) - 1:
        return

    next_pos = pos + 1
    next_id = get_id(next_pos)

    in_focus = next_id


def render(id, base_rel_path=None):
    focused = in_focus == id
    markdown = get_markdown(id)
    rendered = md.get_html(markdown, base_rel_path)

    return render_template(
            "partials/block.html",
            focused=focused,
            id=id,
            markdown=markdown,
            markdown_html=rendered,
            )


def render_all(base_rel_path=None):
    all_block_html = []
    for id in order:
        block_html = render(id, base_rel_path)
        all_block_html.append(block_html)
    blocks_html = "\n".join(all_block_html)
    return render_template(
            "partials/blocks.html",
            ordered_blocks=blocks_html,
            )


def insert(id, base_rel_path=None):
    new_id = create_id()
    set_markdown("", new_id)

    pos = get_pos(id)
    insert_into_order(new_id, pos+1)

    curr_block = render(id, base_rel_path)
    next_block = render(new_id, base_rel_path)
    return "\n".join([curr_block, next_block])


def delete(id):
    remove_markdown(id)
    remove_from_order(id)

    return ""


def set_all_markdown(contents):
    global all_markdown, order, reverse_order
    all_markdown = {}
    order = []
    reverse_order = {}

    blocks = contents.split("\n\n\n")
    for i, b in enumerate(blocks):
        id = create_id()
        all_markdown[id] = b
        order.append(id)
        reverse_order[id] = i

    id = create_id()
    all_markdown[id] = ""
    order.append(id)
    reverse_order[id] = len(blocks)


def get_all_markdown():
    return "\n\n\n".join([v for v in all_markdown.values() if v != ''])
