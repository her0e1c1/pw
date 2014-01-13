# -*- coding: utf-8 -*-
import os
import sys
import argparse
import collections
from getpass import getpass

import model
import api
from .loader import config, set_session


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
    master_key = "1111aa"  # getpass("master key> ")
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

        with model.session_scope() as session:
            set_session(session)
            for command_name in [a for a in dir(args) if not(a.startswith("_"))]:
                if getattr(args, command_name):
                    cmd = getattr(api, command_name)
                    rv = cmd()
                    if rv:
                        session.add(rv)


if __name__ == "__main__":
    m = main()
