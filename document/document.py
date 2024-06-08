import argparse
import os
import socket
import sys

import app
from settings import Settings


def find_port():
  min_port = Settings.MIN_PORT
  max_port = Settings.MAX_PORT

  for port in range(min_port, max_port+1):
    s = socket.socket()
    success = True
    try:
      s.bind(("127.0.0.1", port))
    except OSError:
      success = False

    if success:
      s.close()
      return port

  raise Exception(f"Could not find usable port in range {min_port} to {max_port}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog="document",
            description="edit a markdown document",
            )

    parser.add_argument(
            '-p',
            '--port',
            type=int,
            default=0,
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

    port = args.port
    if args.port == 0:
      port = find_port()
    print(f"Serving on port {port}")

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
            port=port,
            wiki_path=wiki_path,
            one_off_file=file_path
            )
