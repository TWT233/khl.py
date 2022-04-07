import os.path
import pkgutil
import sys
from argparse import ArgumentParser


def entry_point():
    if len(sys.argv) == 1:
        run_bot()
        return

    parser = ArgumentParser(
        prog='khl',
        description='khl.py CLI'
    )
    subparsers = parser.add_subparsers(title='Command', help='Available commands', dest='subparser_name')
    subparsers.add_parser('start', help='start khl.py')
    subparsers.add_parser('init', help='Prepare the working environment of khl.py.')

    result = parser.parse_args()
    if result.subparser_name == 'start':
        run_bot()
    elif result.subparser_name == 'init':
        init_bot()


def environment_check():
    if not os.path.exists('config'):
        return False
    if not os.path.exists('plugin'):
        return False
    if not os.path.exists('config.yml'):
        return False
    return True


def run_bot():
    if not environment_check():
        raise Exception('Use "python -m khl init" to initialize khl.py first')


def initialize_environment():
    if not os.path.exists('config'):
        os.mkdir('config')
    if not os.path.exists('plugin'):
        os.mkdir('plugin')
    if not os.path.exists('config.yml'):
        data = pkgutil.get_data('khl', 'resources/default_config.yml')
        with open('config.yml', 'wb') as f:
            f.write(data)


def init_bot():
    initialize_environment()
