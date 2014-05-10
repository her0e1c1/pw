# -*- coding: utf-8 -*-
import argparse
from getpass import getpass

import api
from .loader import config


def parser(input_string):
    if not input_string.startswith("-"):
        input_string = "-" + input_string

    p = argparse.ArgumentParser(
        add_help=False,
    )
    p.add_argument("-c", "--create-account", action="store_true")
    p.add_argument("-s", "--show_all", action="store_true")
    p.add_argument("-m", "--change-master-key", action="store_true")
    p.add_argument("-p", "--change-password", action="store_true")
    p.add_argument("-d", "--delete-by-id", action="store_true")
    p.add_argument("--delete-all-accounts", action="store_true")
    p.add_argument("-q", "--quit", action="store_true")

    args = p.parse_args(input_string.split())

    return args


def main():
    master_key = getpass("master key> ")
    config["master_key"] = master_key

    while True:
        try:
            args = parser(raw_input("> "))
        except (KeyboardInterrupt, EOFError):
            break
        except SystemExit:
            # show usage and try again
            continue

        if args.quit:
            break

        for command_name in [a for a in dir(args) if not(a.startswith("_"))]:
            if getattr(args, command_name):
                cmd = getattr(api, command_name)
                cmd()


if __name__ == "__main__":
    main()
