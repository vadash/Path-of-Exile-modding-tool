#!/usr/bin/python3
import binascii
import sys
import time
import re
import os

def execute(filename, backupfiledata, modifyggpk):
    filedata, encoding, bom = modifyggpk.stringcleanup(backupfiledata, "UTF-16-LE")
    filedatamod = filedata
    filedatamod = re.sub(r"""\s*"player_light":\s* # key elem
                             [^}]* # body
                             },\s*""", # end 
                         r""""player_light":{"shadows_enabled":false,"colour":[1.0,1.0,1.0],"intensity":1.0,"penumbra":0.0},""",
                         filedatamod,
                         flags=re.IGNORECASE|re.VERBOSE)
    return filedatamod, encoding, bom
