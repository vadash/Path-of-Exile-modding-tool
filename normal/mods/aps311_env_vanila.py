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

    # replace low light
    match = re.search(r'multiplier": ([\d.]*)', filedatamod, flags=re.IGNORECASE)
    if match:
        value = float(match.group(1))
        if value < 1.0:
            filedatamod = re.sub(r"""^\s*"directional_light":\s* # key elem
                                     [^}]* # body
                                     },\s*""", # end 
                                 r""""directional_light":{"shadows_enabled":true,"colour":[1.0,1.0,1.0],"multiplier":0.4,"phi":2,"theta":2},""",
                                 filedatamod,
                                 flags=re.MULTILINE|re.IGNORECASE|re.VERBOSE)
            filedatamod = re.sub(r"""\s*"player_light":\s* # key elem
                                     [^}]* # body
                                     },\s*""", # end 
                                 r""""player_light":{"shadows_enabled":true,"colour":[1.0,1.0,1.0],"intensity":1.0,"penumbra":0.0},""",
                                 filedatamod,
                                 flags=re.IGNORECASE|re.VERBOSE)
    
    return filedatamod, encoding, bom
