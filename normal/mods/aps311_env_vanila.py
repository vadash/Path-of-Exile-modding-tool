#!/usr/bin/python3
import binascii
import sys
import time
import re
import os

def execute(filename, backupfiledata, modifyggpk):
    filedata, encoding, bom = modifyggpk.stringcleanup(backupfiledata, "UTF-16-LE")
    filedatamod = filedata

    # fog? nope
    filedatamod = re.sub(r"""^\s*"fog":\s* # key elem
                             [^}]* # body
                             },\s*""", # end 
                         r'',
                         filedatamod,
                         flags=re.MULTILINE|re.IGNORECASE|re.VERBOSE)

    # cuck bloom
    filedatamod = re.sub(r"""^\s*"post_processing":\s* # key elem
                             [^}]* # body
                             },\s*""", # end 
                         r'',
                         filedatamod,
                         flags=re.MULTILINE|re.IGNORECASE|re.VERBOSE)

    # disable rain
    filedatamod = re.sub(r'Metadata/Effects/weather_attachments/rain/rain.ao', # end 
                         r'',
                         filedatamod,
                         flags=re.MULTILINE|re.IGNORECASE|re.VERBOSE)

    # replace player light with uniform white 
    filedatamod = re.sub(r"""\s*"player_light":\s* # key elem
                             [^}]* # body
                             },\s*""", # end 
                         r""""player_light":{"shadows_enabled":false,"colour":[1.0,1.0,1.0],"intensity":1.0,"penumbra":0.0},""",
                         filedatamod,
                         flags=re.IGNORECASE|re.VERBOSE)

    # add global lighting 2
    match = re.search(r'multiplier": ([\d.]*)', filedatamod, flags=re.IGNORECASE)
    if match:
        value = float(match.group(1))
        new_min = 0.5
        new_max = max(value, 2.5)
        value = ((value / new_max) * (new_max - new_min)) + new_min
        value = max(new_min, value)
        value = min(value, new_max)
        filedatamod = re.sub(r'"multiplier": ([\d.]*)', r'"multiplier": ' + str(value), filedatamod)

    return filedatamod, encoding, bom
