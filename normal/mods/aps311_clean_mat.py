#!/usr/bin/python3
import binascii
import sys
import time
import re
import os

def execute(filename, backupfiledata, modifyggpk):
    filedata, encoding, bom = modifyggpk.stringcleanup(backupfiledata, "UTF-16-LE")
    match = re.search(r"""Version 3""", filedata, flags=re.IGNORECASE)
    if match == None:
    	return None, None, None

    filedatamod = filedata
    filedatamod = re.sub(r"""^effect.*$""",
                         r'',
                         filedatamod,
                         flags=re.MULTILINE|re.IGNORECASE|re.VERBOSE)
    return filedatamod, encoding, bom

