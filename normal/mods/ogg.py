#!/usr/bin/python3
import binascii
import sys
import time
import re
import os
import threading
import queue

displaylabel=""

masterfilter_restrict=[
        "\.ogg$"
    ]

masterfilter_exclude=[
    ]

with open(os.path.join("assets", "minimal.ogg"), "rb") as fin :
   minimal_ogg=fin.read()

def execute(filename, backupfiledata, modifyggpk):
   return minimal_ogg, None, None
