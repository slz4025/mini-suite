# mini-suite 

## What is it?

mini-suite is a (planned) set of collaborative tools inspired by the likes
of <a href="https://www.office.com/">Microsoft Office</a>
or <a href="https://workspace.google.com/">Google Workspace</a>.
The following tools are planned for development:
- Spreadsheet
- Editor
- File system
- [maybe] Meetings

Whereas Microsoft Office or Google Workspace offer a ton of features,
mini-suite aims to:
1. provide essential features, as judged by my family,
2. deliver a simple, accessible, and performant experience,
3. be usable from most browsers and operating systems.

## What does it currently support?

This is still in active development.
I am currently working on the spreadsheet.

## Why are you doing this?

1. Because it's fun and I'm learning a lot.
2. Because I want a good user experience on my machine.

## How do I try it out?

Setup the environment:
```
cd {spreadsheet|document}
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the server:
```
python {spreadsheet|document}/app.py
```

Visit `localhost:5000` in your browser and interact with the webpage.

## How does this work?

This runs as a web application so it can be usable from any operating system.
It uses HTML/CSS that I would expect to be compatible with most browsers.

I'm testing this with <a href="https://www.qutebrowser.org/">qutebrowser</a>
on <a href="https://www.openbsd.org/73.html">OpenBSD 7.3</a>.

This is written mostly in <a href="https://www.python.org/">Python 3</a>
using <a href="https://flask.palletsprojects.com/en/3.0.x/">flask</a>
and <a href="https://htmx.org/">htmx</a>.
