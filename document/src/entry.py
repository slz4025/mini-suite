from flask import render_template
import os
from typing import Dict, List, Optional
import uuid

import src.markdown as md


class Entry:
    def __init__(self, entry_id, file_path):
        if not file_path.endswith(".md"):
            raise Exception(f"File path '{file_path}' is not a markdown file.")

        self.id = entry_id

        self.file_path: str = file_path
        self.block_in_focus: Optional[str] = None
        self.block_order: List[str] = []
        self.reverse_block_order: Dict[str, int] = {}
        self.all_block_markdown: Dict[str, str] = {}

        contents = ""
        if os.path.isfile(self.file_path):
            with open(self.file_path, 'r') as file:
                contents = file.read()

        all_block_markdown = contents.split("\n\n\n")
        for i, block_markdown in enumerate(all_block_markdown):
            block_id = uuid.uuid4().hex
            self.all_block_markdown[block_id] = block_markdown
            self.block_order.append(block_id)
            self.reverse_block_order[block_id] = i

        # make one extra block
        block_id = uuid.uuid4().hex
        self.all_block_markdown[block_id] = ""
        self.block_order.append(block_id)
        self.reverse_block_order[block_id] = len(all_block_markdown)

    def get_file_path(self):
        return self.file_path

    def get_dir(self):
        dir, basename = os.path.split(self.file_path)
        return dir

    def get_name(self):
        dir, basename = os.path.split(self.file_path)
        return basename

    def get_html(self, block_id):
        markdown = self.get_markdown(block_id)
        html = md.get_html(markdown, self.get_dir())
        return html

    def get_markdown(self, block_id):
        if block_id not in self.all_block_markdown:
            raise Exception(f"Block id '{block_id}' does not exist.")
        return self.all_block_markdown[block_id]

    def set_markdown(self, block_id, markdown):
        self.all_block_markdown[block_id] = markdown

    def remove_markdown(self, block_id):
        del self.all_block_markdown[block_id]

    def get_in_focus(self):
        return self.block_in_focus

    def set_in_focus(self, block_id):
        self.block_in_focus = block_id

    def reset_in_focus(self):
        self.block_in_focus = None

    def get_id(self, pos):
        if pos < 0 or pos >= len(self.block_order):
            raise Exception(f"Position {pos} is not valid.")
        return self.block_order[pos]

    def get_pos(self, block_id):
        if block_id not in self.reverse_block_order:
            raise Exception(f"Block id '{block_id}' does not have a position.")
        return self.reverse_block_order[block_id]

    def edit_block(self, contents):
        self.set_markdown(self.block_in_focus, contents)

    def unfocus_block(self):
        block_id = self.block_in_focus
        self.reset_in_focus()
        return block_id

    def focus_next_block(self):
        pos = self.get_pos(self.block_in_focus)

        if pos == len(self.block_order) - 1:
            return

        next_pos = pos + 1
        next_id = self.get_id(next_pos)

        self.block_in_focus = next_id
        return self.block_in_focus

    def focus_prev_block(self):
        pos = self.get_pos(self.block_in_focus)

        if pos == 0:
            return

        prev_pos = pos - 1
        prev_id = self.get_id(prev_pos)

        self.block_in_focus = prev_id
        return self.block_in_focus

    def insert_block(self):
        new_id = uuid.uuid4().hex
        new_pos = self.get_pos(self.block_in_focus) + 1

        self.set_markdown(new_id, "")
        self.block_order = \
            self.block_order[:new_pos] + [new_id] + self.block_order[new_pos:]
        self.reverse_block_order[new_id] = new_pos
        # shift-right everything after
        for i in range(new_pos+1, len(self.block_order)):
            temp_id = self.block_order[i]
            assert i == self.reverse_block_order[temp_id] + 1
            self.reverse_block_order[temp_id] = i

        return new_id

    def delete_block(self):
        pos = self.get_pos(self.block_in_focus)

        self.remove_markdown(self.block_in_focus)
        self.block_order = self.block_order[:pos] + self.block_order[pos+1:]
        del self.reverse_block_order[self.block_in_focus]
        # shift-right everything after
        for i in range(pos, len(self.block_order)):
            temp_id = self.block_order[i]
            assert i == self.reverse_block_order[temp_id] - 1
            self.reverse_block_order[temp_id] = i

        self.reset_in_focus()

    def render_block(self, block_id):
        focused = self.block_in_focus == block_id
        markdown = self.get_markdown(block_id)
        rendered = self.get_html(block_id)

        return render_template(
                "partials/block.html",
                focused=focused,
                entry_id=self.id,
                block_id=block_id,
                markdown=markdown,
                markdown_html=rendered,
                )

    def render_null(self):
        return render_template(
                "partials/null.html",
                )

    def render_banner(self, show_saved=False):
        return render_template(
                "partials/banner.html",
                entry_id=self.id,
                show_saved=show_saved,
                )

    def render(self, dark_mode):
        null_html = self.render_null()
        banner_html = self.render_banner(show_saved=False)

        all_block_html = []
        for block_id in self.block_order:
            block_html = self.render_block(block_id)
            all_block_html.append(block_html)

        blocks_html = render_template(
                "partials/blocks.html",
                ordered_blocks="\n".join(all_block_html),
                )

        body_html = render_template(
                "partials/body.html",
                banner=banner_html,
                null=null_html,
                name=self.get_name(),
                blocks=blocks_html,
                )
        return render_template(
                "index.html",
                tab_name=self.get_name(),
                dark_mode=dark_mode,
                body=body_html,
                )

    def save(self):
        all_markdown = "\n\n\n".join(
            [v for v in self.all_block_markdown.values() if v != '']
        )
        with open(self.file_path, 'w+') as file:
            file.write(all_markdown)
