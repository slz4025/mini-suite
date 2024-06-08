from flask import render_template

import src.sheet as sheet

import src.selector.types as types


text = ""


def set_text(_text):
    global text
    text = _text


def reset_text():
    global text
    text = ""


def render_result(row, col, value):
    return render_template(
            "partials/selector/search/result.html",
            row=row,
            col=col,
            data=value,
    )


def render_results():
    if text == "":
      return ""

    results = sheet.get_cells_containing_text(text)

    entries = []
    for p in results:
      row = p.row_index.value
      col = p.col_index.value
      value = sheet.get_cell_computed(p)
      result_html = render_result(row, col, value)
      entries.append(result_html)
    
    return "\n".join(entries)


def render():
    # reset upon re-render
    reset_text()
    results = render_results()

    return render_template(
            "partials/selector/search.html",
            results=results,
    )
