import argparse
import os
import socket
import sys

from app import start
from settings import Settings

from src.state import setup


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

    raise Exception(
        f"Could not find usable port in range {min_port} to {max_port}."
    )


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
    parser.add_argument(
            'path',
            type=str,
            help="File path to markdown file."
            )

    args = parser.parse_args(sys.argv[1:])

    path = os.path.abspath(args.path)
    setup(path)

    port = args.port
    if args.port == 0:
        port = find_port()
    print(f"Serving on port {port}")

    start(port=port)
