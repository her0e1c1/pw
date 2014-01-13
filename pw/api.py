# -*- coding: utf-8 -*-
import os
import sys
import collections
import tempfile
from getpass import getpass

from .model import Account
from .encrypt import encrypt, decrypt
from .utils import ask_yes_or_no


__all__ = ["show_all", "create_account", "change_password"]

def show_all():
    """ print information about all acounts. """
    buff = ["id, account, password, name"]
    buff.append("-" * 100)
    for a in Account.query():
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
    return Account.create(account, password, name)


def change_password(self, target_account=None, old_password=None, new_password=None):
    """change a password of the target_account into a new password"""
    if target_account is None:
        target_account = raw_input("account> ")
    if old_password is None:
        old_password = getpass("old password> ")
    if new_password is None:
        new_password = getpass("new password> ")

    if not Account.exists(account=target_account):
        raise ValueError("%s doesn't exits" % target_account) 

    id, account, password, name = self.search_account(target_account)
    if password == old_password:
        self._session_delete(self._delete(id))
        self._session_add(self._create(account, new_password, name))
    else:
        print("%s doesn't match the registered password" % old_password)


def change_master_key(new_master_key=None):
    if new_master_key is None:
        new_key = getpass("new master key> ")
    new_aes = AES.new(self.format % new_key)
    return Account.update(new_key=new_key)


def delete_all_accounts():
    if ask_yes_or_no("Delete all accounts. Are you sure?[y/N]"):
        return Account.delete_all()


def delete_by_id(id=None):
    id = int(raw_input("delete id> "))
    if ask_yes_or_no("Delete %d account. Are you sure?[y/N]" % id):
        return Account.delete(id)
