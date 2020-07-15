import brotli
import kivy_img_dds

def execute(filename, filedata, modifyggpk):
    if filedata[0] == ord("*") and filedata[3]>=0x20 :
        return None, None, None
    filedataOrig = filedata

    if filedata[:4] != b'DDS ' :
        reencodeneeded=True
        size = int.from_bytes(filedata[:4], 'little')
        filedata = brotli.decompress(filedata[4:])
        if len(filedata)!=size :
            print("Error wrong size after brotli decode %s" % (filename))
            return None, None, None

    try :
        dds = kivy_img_dds.DDSFile(filedata)
        tmp = dds.stripratiomipmap(2)
        if 1.10 * len(tmp) + 1000 < len(filedataOrig):
            # all good (more than 10% saving)
            return tmp, None, None
        else :
            # using original
            return None, None, None

    except Exception as e :
        print("%s %s" % (str(e), filename))
        return None, None, None

    return None, None, None
