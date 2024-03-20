# mini-suite 

## What is it?

mini-suite is a (planned) set of collaborative tools inspired by the likes of [Microsoft Office](https://www.office.com/) or [Google Workspace](https://workspace.google.com/). The following tools are planned for development:
- Markdown editor
- Spreadsheet editor

Whereas Microsoft Office or Google Workspace offer a ton of features,
mini-suite aims to:
1. provide essential features, as judged by my family,
2. deliver a simple, accessible, and performant experience,
3. be usable from most browsers and operating systems.

## What does it currently support?

This is still in active development. I have mostly finished the markdown editor and am currently working on the spreadsheet editor.

## How do I use the markdown editor?

The markdown editor allows you to create a wiki of inter-linking markdown files.

Setup the environment:
```
cd document
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the server:
```
python document/app.py <path to wiki folder>
```

Visit `localhost:5000` in your browser and interact with the webpage.

## How do I use the spreadsheet editor?

The spreadsheet editor allows you to manipulate table-based data via a GUI.

Setup the environment:
```
cd spreadsheet
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the server:
```
python spreadsheet/app.py
```

Visit `localhost:5000` in your browser and interact with the webpage.

## How does this work?

The tools run as a web application so that they can be usable from any operating system. It uses HTML/CSS that I would expect to be compatible with most browsers.

I'm testing this with [qutebrowser](https://www.qutebrowser.org/) on [OpenBSD 7.3](https://www.openbsd.org/73.html).

This is written mostly in [Python 3](https://www.python.org/) using [flask](https://flask.palletsprojects.com/en/3.0.x/) and [htmx](https://htmx.org/). The markdown processor I'm using is the Python port of [markdown-it](https://github.com/markdown-it/markdown-it).
