#!/usr/bin/python3
import binascii
import sys
import time
import re
import os

def execute(filename, backupfiledata, modifyggpk):
   filedata, encoding, bom = modifyggpk.stringcleanup(backupfiledata, "UTF-16-LE")
   filedatamod=re.sub(r'Life[\t\r\n ]*\{.*?\}[\t\r ]*(\n|$)', r'Life\r\n{\r\n\ton_spawned_dead = "DisableRendering();"\r\n\ton_death = "DisableRendering();"\r\n}\r\n', filedata, flags=re.DOTALL)
   return filedatamod, encoding, bom

