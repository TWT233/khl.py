import sys

from .cli.cli_entry import entry_point


def main():
    entry_point()


if __name__ == '__main__':
    sys.exit(main())
