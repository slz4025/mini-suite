import argparse
import sys


import app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog="spreadsheet",
            description="manipulate a CSV spreadsheet",
            )

    parser.add_argument(
            '-p',
            '--port',
            type=int,
            default=5000,
            help="port for application to run on",
            )

    parser.add_argument(
            'path',
            type=str,
            help="File path to CSV."
            )

    parser.add_argument(
            '--debug',
            action="store_true",
            default=False,
            help="debug mode"
            )

    args = parser.parse_args(sys.argv[1:])
    app.start(
            port=args.port,
            path=args.path,
            debug=args.debug,
            )
