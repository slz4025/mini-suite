from flask import render_template

import src.wiki as wiki


def get_operation_path(operation):
    if operation == "open":
        return "open"
    elif operation.startswith("link-to-block-"):
        id = operation.removeprefix("link-to-block-")
        return f"block/{id}/link"
    else:
        raise Exception("'{operation}' is not a known selector operation.")


def get_operation_target(operation):
    if operation == "open":
        return "#null"
    elif operation.startswith("link-to-block-"):
        id = operation.removeprefix("link-to-block-")
        return f"#block-{id}"
    else:
        raise Exception("'{operation}' is not a known selector operation.")


def render_result(session, operation, name):
    path = get_operation_path(operation)
    target = get_operation_target(operation)
    return render_template(
            "partials/entry_result.html",
            name=name,
            path=path,
            target=target,
            )


def render_results(session, operation, search):
    if search == "":
        filtered_names = []
    else:
        valid_entries = [e for e in wiki.entries if not e.startswith("temp-")]
        filtered_names = sorted(
                [e for e in valid_entries if e.startswith(search)]
                )
        num_results = min(5, len(filtered_names))
        filtered_names = filtered_names[:num_results]
    entry_results = [
            render_result(session, operation, name) for name in filtered_names
            ]
    return '\n'.join(entry_results)


def render(session, operation, search=""):
    entry_results = render_results(session, operation, search)
    return render_template(
            "partials/entry_selector.html",
            operation=operation,
            entry_results=entry_results,
            )
