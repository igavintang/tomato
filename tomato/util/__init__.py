'''
FilePath: /tomato/tomato/util/__init__.py
Author: Gavin Tang
LastEditors: Gavin Tang
Description: ...
Date: 2021-01-25 21:35:02
LastEditTime: 2023-06-02 15:30:18
'''

# -*- coding:utf-8 -*-


import os
import codecs
import chardet
import importlib
import configparser
import tornado.autoreload
from .xid import Xid


def autoreload():
    tornado.autoreload.start()

def loadconf(conf_file, raw=False):
    filename = os.path.abspath(conf_file)
    if raw:
        conf = configparser.RawConfigParser()
    else:
        conf = configparser.ConfigParser()
    conf.readfp(codecs.open(filename, "r", "utf8"))
    return conf

def gen_object(module_name, class_name):
    """Generates an object based on module_name(xxx.xxx.xxx) and class_name
    """
    module = importlib.import_module(module_name)
    module_cls = getattr(module, class_name)
    cls_obj = module_cls()
    return cls_obj

def transcoding(text, encoding):
    """transcoding
    """
    textLength = 2048
    if len(text) < 2048:
        textLength = len(text)
    tempText = text[0:textLength]
    decoding = chardet.detect(tempText)['encoding']
    if decoding is None:
        text = text.decode('gbk', 'ignore').encode(encoding)
    elif decoding != 'UTF-8':
        text = text.decode(decoding, 'ignore').encode(encoding)
    return text

from .log import Log
from .typeassert import typeassert
from .singleton import singleton
from .appmodule import AppModule
from .application import Application
