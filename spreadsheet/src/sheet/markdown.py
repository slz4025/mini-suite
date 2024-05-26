from markdown_it import MarkdownIt


md = (
        MarkdownIt('commonmark', {'breaks': True, 'html': True})
        )


def convert_to_html(markdown):
    html = md.render(markdown)
    return html
