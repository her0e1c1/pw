# -*- coding: utf-8 -*-
import os
import sys
import argparse
import collections
from getpass import getpass

import api
from .loader import config


def parser(input_string):
    p = argparse.ArgumentParser()
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
    master_key = config.get("master_key")
    if not master_key:
        master_key = getpass("master key> ")
    config.update({
        "master_key": master_key,
    })

    while True:
        try:
            args = parser(raw_input("> "))
        except:
            continue

        if args.quit:
            break

        for command_name in [a for a in dir(args) if not(a.startswith("_"))]:
            if getattr(args, command_name):
                cmd = getattr(api, command_name)
                cmd()


if __name__ == "__main__":
    m = main()
