#!/usr/bin/python3
import binascii
import sys
import time
import re
import os

displaylabel=""

masterfilter_restrict=[
    ]

masterfilter_exclude=[
    ]

def execute(filename, backupfiledata, modifyggpk):
    filedata, encoding, bom = modifyggpk.stringcleanup(backupfiledata, "UTF-16-LE")
    filedatamod = filedata
    #saving only 1 emitter
    match = re.search(r'({[^}]+})', filedatamod)
    if match:
        filedatamod = "1\r\n" + match.group(1)
    return filedatamod, encoding, bom
