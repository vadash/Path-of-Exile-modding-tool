#!/usr/bin/python3
import binascii
import sys
import time
import re
import os

def execute(filename, backupfiledata, modifyggpk):
    filedata, encoding, bom = modifyggpk.stringcleanup(backupfiledata, "UTF-16-LE")
    filedatamod = filedata
    # keeping first emitter intact
    emitters = filedatamod.split('}', maxsplit=1)
    if len(emitters) != 2:
        return None, None, None
    # making 2+ emitters as short as possible
    emitters[1] = re.sub(r"""^[\W]*anim_play_once [\d. ]*[\W]*$""",
                         r"""\tanim_play_once 1\r""",
                         emitters[1],
                         flags=re.MULTILINE|re.IGNORECASE|re.VERBOSE)
    emitters[1] = re.sub(r"""^[\W]*is_infinite [\d. ]*[\W]*$""",
                         r"""\tis_infinite 0\r""",
                         emitters[1],
                         flags=re.MULTILINE|re.IGNORECASE|re.VERBOSE)

    emitters[1] = re.sub(r"""^[\W]*particle_duration [\d. ]*[\W]*$""",
                         r"""\tparticle_duration 0.005\r""",
                         emitters[1],
                         flags=re.MULTILINE|re.IGNORECASE|re.VERBOSE)
    emitters[1] = re.sub(r"""^[\W]*emitter_duration [\d. ]*[\W]*$""",
                         r"""\temitter_duration 0.005\r""",
                         emitters[1],
                         flags=re.MULTILINE|re.IGNORECASE|re.VERBOSE)

    filedatamod = emitters[0] + "}" + emitters[1]
    return filedatamod, encoding, bom
