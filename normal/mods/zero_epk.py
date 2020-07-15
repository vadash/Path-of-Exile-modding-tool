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
    filedatamod=""
    return filedatamod, encoding, bom

