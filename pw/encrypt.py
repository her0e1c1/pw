# -*- coding: utf-8 -*-
from Crypto.Cipher import AES
from .loader import config


def _make_aes():
    format = config.get("aes_format")
    aes = AES.new(format % config.get("master_key"))
    return aes


def encrypt(x, aes=None):
    if aes is None:
        aes = _make_aes()    
    return aes.encrypt(config.get("aes_format") % x)


def decrypt(x, aes=None):
    if aes is None:
        aes = _make_aes()    
    try:
        return aes.decrypt(x).decode()
    except UnicodeDecodeError:
        return aes.decrypt(x)
