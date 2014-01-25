# -*- coding: utf-8 -*-
import os
import sys
import collections
import tempfile
from getpass import getpass

from .model import Account, autocommit
from .encrypt import encrypt, decrypt
from .utils import ask_yes_or_no
from .loader import config


def show_all():
    """ print information about all acounts. """
    buff = ["id, account, password, description"]
    buff.append("-" * 100)
    for a in Account.query.all():
        buff.append("{0}, {1}, {2}, {3}".format(a.id, a.raw_account, a.raw_password, a.description))

    with tempfile.NamedTemporaryFile("w+t") as tf:
        tf.write("\n".join(buff))
        tf.flush()
        os.system("less {}".format(tf.name))


def create_account(account=None, password=None, name=None):
    """if there is no account on DB, then make it. """
    # intput
    if account is None:
        account = raw_input("account> ")
    if password is None:
        password = getpass("password> ")
    if name is None:
        name = raw_input("description> ")

    return Account.query.create(account, password, name)


def change_password(target_account=None, old_password=None, new_password=None):
    """change a password of the target_account into a new password"""
    if target_account is None:
        target_account = raw_input("account> ")

    a = Account.query.first(account=target_account)
    if not a:
        print("%s doesn't exits" % target_account) 
        return

    if old_password is None:
        old_password = getpass("old password> ")
    if new_password is None:
        new_password = getpass("new password> ")

    if a.raw_password == old_password:
        a.update(raw_password=new_password)
    else:
        print("%s doesn't match the registered password" % old_password)


def change_master_key(new_master_key=None):
    if new_master_key is None:
        new_master_key = getpass("new master key> ")
    for a in Account.query.all():
        a.change_master_key(new_master_key)
    else:
        config.update({
            "master_key": new_master_key,
        })


def delete_all_accounts():
    if ask_yes_or_no("Delete all accounts. Are you sure?[y/N]"):
        Account.query.delete_all()


def delete_by_id(id=None):
    id = int(raw_input("delete id> "))
    if ask_yes_or_no("Delete %d account. Are you sure?[y/N]" % id):
        Account.query.delete(id)
