import argparse
import os
import sys


import app


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

    sub_parsers = parser.add_subparsers(
            dest="subcommand",
            help="mode to use editor"
            )

    wiki_parser = sub_parsers.add_parser(
            "wiki",
            help="edit markdown wiki",
            )
    wiki_parser.add_argument(
            'path',
            type=str,
            help="Directory path to markdown wiki."
            )

    file_parser = sub_parsers.add_parser(
            "file",
            help="edit one-off markdown file"
            )
    file_parser.add_argument(
            'path',
            type=str,
            help="File path to one-off file."
            )

    args = parser.parse_args(sys.argv[1:])
    subcommand = args.subcommand

    wiki_path = None
    file_path = None
    match subcommand:
        case "wiki":
            wiki_path = os.path.abspath(args.path)
        case "file":
            file_path = os.path.abspath(args.path)
        case _:
            if subcommand is None:
                raise Exception("Subcommand not specified.")
            else:
                raise Exception(f"Unknown subcommand {subcommand}.")

    app.start(
            port=args.port,
            wiki_path=wiki_path,
            one_off_file=file_path
            )
