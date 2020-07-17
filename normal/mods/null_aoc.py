import re

def execute(filename, backupfiledata, modifyggpk):
    filedata, encoding, bom = modifyggpk.stringcleanup(backupfiledata, "UTF-16-LE")
    filedatamod=filedata
    mi=re.finditer(r'(\w+)[\t\r\n ]*\{.*?\}[\t\r ]*(\n|$)', filedata, flags=re.DOTALL)
    for mii in mi :
        tagis=mii.group(1)
        filedatamod=re.sub(tagis+r'[\t\r\n ]*\{.*?\}[\t\r ]*(\n|$)', tagis+r'\r\n{\r\n}\r\n', filedatamod, flags=re.DOTALL)
    return filedatamod, encoding, bom