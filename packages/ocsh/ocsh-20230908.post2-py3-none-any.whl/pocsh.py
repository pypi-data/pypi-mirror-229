#!/usr/bin/env python3

# 2023 Laurent Ghigonis <ooookiwi@gmail.com>

import sys
import logging
import argparse
from pathlib import Path

from ocsh import Sshconf

DESCRIPTION = """ """
EXAMPLES = """$ pocsh list '_net1_*'
$ pocsh ig '_net1_*'
"""

def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION, epilog=EXAMPLES, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-F', '--ssh-config', default=Sshconf.CONFPATH_DEFAULT, help=argparse.SUPPRESS)
    parser.add_argument('-v', '--verbose', action='store_const', dest="loglevel", const=logging.DEBUG, default=logging.INFO, help="enable debug messages")
    subparsers = parser.add_subparsers(dest='action', help='action')

    subp = subparsers.add_parser('examples', help='show usage examples')

    subp = subparsers.add_parser('list', help='list ssh aliases matching patterns')
    subp.add_argument('patterns', nargs='+', help='')

    subp = subparsers.add_parser('ig', help='information gathering')

    args = parser.parse_args()

    if args.action == 'examples':
        print("pocsh examples:\n\n"+EXAMPLES)
        exit()

    logging.basicConfig(level=args.loglevel, format='ocsh: %(message)s')

    c = Sshconf(Path(args.ssh_config))


if __name__ == "__main__":
    sys.exit(main())
