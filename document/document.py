import argparse
import os
import sys


import app


DEFAULT_DIR = os.path.expanduser("~/.minisuite/documents")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog="document",
            description="edit a markdown document",
            )

    parser.add_argument(
            '-p',
            '--port',
            type=int,
            default=5000,
            help="port for application to run on",
            )

    parser.add_argument(
            '-w',
            '--wiki-path',
            type=str,
            default=DEFAULT_DIR,
            help="Path to create markdown wiki in. "
            "If not specified, will use default, non-wiki path.",
            )

    args = parser.parse_args(sys.argv[1:])
    app.start(args.port, args.wiki_path)
