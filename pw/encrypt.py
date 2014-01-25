# -*- coding: utf-8 -*-
from Crypto.Cipher import AES
from .loader import config


def _make_aes(master_key=None):
    format = config.get("aes_format")
    if master_key is None:
        master_key = config.get("master_key")
    aes = AES.new(format % master_key)
    return aes


def encrypt(x, master_key=None):
    aes = _make_aes(master_key=master_key)
    return aes.encrypt(config.get("aes_format") % x)


def decrypt(x, aes=None):
    if aes is None:
        aes = _make_aes()    
    try:
        return aes.decrypt(x).decode()
    except UnicodeDecodeError:
        return aes.decrypt(x)
