import re

'''

restriction "\.ao$"

'''

condition=[
    "AttachedAnimatedObject",
    ]

def execute(filename, backupfiledata, modifyggpk):
    filedata, encoding, bom = modifyggpk.stringcleanup(backupfiledata, "UTF-16-LE")
    filedatamod=filedata
    mi=re.finditer(r'((\w+)[\t\r\n ]*\{.*?\}[\t\r ]*(\n|$))', filedatamod, flags=re.DOTALL)
    for mii in mi :
        tagis=mii.group(2)
        if tagis in condition :
            filedatamod=re.sub(tagis+r'[\t\r\n ]*\{.*?\}[\t\r ]*(\n|$)', tagis+r'\r\n{\r\n}\r\n', filedatamod, flags=re.DOTALL)
    return filedatamod, encoding, bom
