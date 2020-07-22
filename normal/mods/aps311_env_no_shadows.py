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
    filedatamod = re.sub(r"""^\s*"area":\s* # key elem
                             [^}]* # body
                             },\s*""", # end 
                         r'',
                         filedatamod,
                         flags=re.MULTILINE|re.IGNORECASE|re.VERBOSE)

    # disable shadows
    filedatamod = re.sub(r'"shadows_enabled": true,', r'"shadows_enabled": false,', filedatamod)
    filedatamod = re.sub(r'"use_forced_screenspace_shadows": true,', r'"use_forced_screenspace_shadows": false,', filedatamod)

    # replace player light with uniform white 
    filedatamod = re.sub(r"""\s*"player_light":\s* # key elem
                             [^}]* # body
                             },\s*""", # end 
                         r""""player_light":{"shadows_enabled":false,"colour":[1.0,1.0,1.0],"intensity":1.0,"penumbra":0.0},""",
                         filedatamod,
                         flags=re.IGNORECASE|re.VERBOSE)

    # add global lighting
    match = re.search(r'env_brightness": ([\d.]*)', filedatamod, flags=re.IGNORECASE)
    if match:
        env_brightness = float(match.group(1))
        min_value = 1.0
        max_value = max(env_brightness, 2.5)
        env_brightness = ((env_brightness / 2.5) * 1.5) + 1 # 0..2.5 -> 1..2.5
        env_brightness = max(min_value, env_brightness)
        env_brightness = min(env_brightness, max_value)
        filedatamod = re.sub(r'"env_brightness": ([\d.]*)', r'"env_brightness": ' + str(env_brightness), filedatamod)

    return filedatamod, encoding, bom
