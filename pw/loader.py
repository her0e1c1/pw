# -*- coding: utf-8 -*-
import os
try:
    import configparser
except ImportError:
    import ConfigParser as configparser


config = {
    "url":"sqlite:////" + os.getcwd() + "test.db",
    "master_key":"1111",
    "aes_format": "%32s"
}

# MYCONFIGPATH = os.environ.get("MYCONFIGPATH")
# if MYCONFIGPATH is None:
#     MYCONFIGPATH = "myconfig.ini"

# if not os.path.isfile(MYCONFIGPATH):
#     raise ImportError("myconfig.ini can't be imported.")
#MYCONFIG = IniFileReader(MYCONFIGPATH)
