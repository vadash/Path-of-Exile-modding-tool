'''
DDS File library
================

This library can be used to parse and save DDS
(`DirectDraw Surface <https://en.wikipedia.org/wiki/DirectDraw_Surface>`)
files.

The initial version was written by::

    Alexey Borzenkov (snaury@gmail.com)

All the initial work credits go to him! Thank you :)

This version uses structs instead of ctypes.


DDS Format
----------

::

    [DDS ][SurfaceDesc][Data]

    [SurfaceDesc]:: (everything is uint32)
        Size
        Flags
        Height
        Width
        PitchOrLinearSize
        Depth
        MipmapCount
        Reserved1 * 11
        [PixelFormat]::
            Size
            Flags
            FourCC
            RGBBitCount
            RBitMask
            GBitMask
            BBitMask
            ABitMask
        [Caps]::
            Caps1
            Caps2
            Reserved1 * 2
        Reserverd2

.. warning::

    This is an external library and Kivy does not provide any support for it.
    It might change in the future and we advise you don't rely on it in your
    code.

'''

import math
from struct import pack, unpack, calcsize

# DDSURFACEDESC2 dwFlags
DDSD_CAPS                  = 0x00000001
DDSD_HEIGHT                = 0x00000002
DDSD_WIDTH                 = 0x00000004
DDSD_PITCH                 = 0x00000008
DDSD_PIXELFORMAT           = 0x00001000
DDSD_MIPMAPCOUNT           = 0x00020000
DDSD_LINEARSIZE            = 0x00080000
DDSD_DEPTH                 = 0x00800000

# DDPIXELFORMAT dwFlags
DDPF_ALPHAPIXELS           = 0x00000001
DDPF_FOURCC                = 0x00000004
DDPF_RGB                   = 0x00000040
DDPF_LUMINANCE             = 0x00020000

# DDSCAPS2 dwCaps1
DDSCAPS_COMPLEX            = 0x00000008
DDSCAPS_TEXTURE            = 0x00001000
DDSCAPS_MIPMAP             = 0x00400000

# DDSCAPS2 dwCaps2
DDSCAPS2_CUBEMAP           = 0x00000200
DDSCAPS2_CUBEMAP_POSITIVEX = 0x00000400
DDSCAPS2_CUBEMAP_NEGATIVEX = 0x00000800
DDSCAPS2_CUBEMAP_POSITIVEY = 0x00001000
DDSCAPS2_CUBEMAP_NEGATIVEY = 0x00002000
DDSCAPS2_CUBEMAP_POSITIVEZ = 0x00004000
DDSCAPS2_CUBEMAP_NEGATIVEZ = 0x00008000
DDSCAPS2_VOLUME            = 0x00200000

# Common FOURCC codes
DDS_DXTN = 0x00545844
DDS_DXT1 = 0x31545844
DDS_DXT2 = 0x32545844
DDS_DXT3 = 0x33545844
DDS_DXT4 = 0x34545844
DDS_DXT5 = 0x35545844
ATI1 = 0x31495441
ATI2 = 0x32495441
RXGB = 0x42475852
DOLLARNULL = 0x24
oNULL = 0x6f
pNULL = 0x70
qNULL = 0x71
rNULL = 0x72
sNULL = 0x73
tNULL = 0x74

# BIT4 = 17 * index
BIT5 = [0,8,16,25,33,41,49,58,66,74,82,90,99,107,115,123,132,140,148,156,165,173,181,189,197,206,214,222,230,239,247,255]
BIT6 = [0,4,8,12,16,20,24,28,32,36,40,45,49,53,57,61,65,69,73,77,81,85,89,93,97,101,105,109,113,117,121,125,130,134,138,142,146,150,154,158,162,166,170,174,178,182,186,190,194,198,202,206,210,215,219,223,227,231,235,239,243,247,251,255]

# def dxt_to_str(dxt):
#     if dxt == DDS_DXT1:
#         return 's3tc_dxt1'
#     elif dxt == DDS_DXT2:
#         return 's3tc_dxt2'
#     elif dxt == DDS_DXT3:
#         return 's3tc_dxt3'
#     elif dxt == DDS_DXT4:
#         return 's3tc_dxt4'
#     elif dxt == DDS_DXT5:
#         return 's3tc_dxt5'
#     elif dxt == 0:
#         return 'rgba'
#     elif dxt == 1:
#         return 'alpha'
#     elif dxt == 2:
#         return 'luminance'
#     elif dxt == 3:
#         return 'luminance_alpha'
#
# def str_to_dxt(dxt):
#     if dxt == 's3tc_dxt1':
#         return DDS_DXT1
#     if dxt == 's3tc_dxt2':
#         return DDS_DXT2
#     if dxt == 's3tc_dxt3':
#         return DDS_DXT3
#     if dxt == 's3tc_dxt4':
#         return DDS_DXT4
#     if dxt == 's3tc_dxt5':
#         return DDS_DXT5
#     if dxt == 'rgba':
#         return 0
#     if dxt == 'alpha':
#         return 1
#     if dxt == 'luminance':
#         return 2
#     if dxt == 'luminance_alpha':
#         return 3

def PixelFormatToBpp(pixelformat, rgbbitcount) :
    if pixelformat == 'LUMINANCE' :
        return rgbbitcount // 8
    elif pixelformat == 'LUMINANCE_ALPHA' :
        return rgbbitcount // 8
    elif pixelformat == 'RGBA' :
        return rgbbitcount // 8
    elif pixelformat == 'RGB' :
        return rgbbitcount // 8
    elif pixelformat == 'THREEDC' :
        return 3
    elif pixelformat == 'RXGB' :
        return 3
    elif pixelformat == 'ATI1N' :
        return 1
    elif pixelformat == 'R16F' :
        return 2
    elif pixelformat == 'A16B16G16R16' :
        return 8
    elif pixelformat == 'A16B16G16R16F' :
        return 8
    elif pixelformat == 'G32R32F' :
        return 8
    elif pixelformat == 'A32B32G32R32F' :
        return 16
    else :
        return 4

def PixelFormatToBpc(pixelformat) :
    if pixelformat == 'R16F' :
        return 4
    elif pixelformat == 'G16R16F' :
        return 4
    elif pixelformat == 'A16B16G16R16F' :
        return 4
    elif pixelformat == 'R32F' :
        return 4
    elif pixelformat == 'G32R32F' :
        return 4
    elif pixelformat == 'A32B32G32R32F' :
        return 4
    elif pixelformat == 'A16B16G16R16' :
        return 2
    else :
        return 1

def multiply(component, multiplier):
    if multiplier==0 :
        return 0
    return int(component * multiplier)

# def align_value(val, b):
#     return val + (-val % b)

def check_flags(val, fl):
    return (val & fl) == fl

# def dxt_size(w, h, dxt):
#     w = int(math.floor((w+3)/4))
#     h = int(math.floor((h+3)/4))
#     #w = max(1, w // 4)
#     #h = max(1, h // 4)
#     if dxt == DDS_DXT1:
#         return w * h * 8
#     elif dxt in (DDS_DXT2, DDS_DXT3, DDS_DXT4, DDS_DXT5):
#         return w * h * 16
#     return -1

def ComputeMaskParams(mask):
    shift1 = 0
    mul = 1
    shift2 = 0
    if (mask == 0 or mask == 0xffffffff) :
        return shift1, mul, shift2
    while (mask & 1) == 0 :
        mask = mask >> 1
        shift1+=1
    bc = 0
    while (mask & (1 << bc)) != 0 :
        bc+=1
    while (mask * mul) < 255 :
        mul = (mul << bc) + 1
    mask *= mul
    while (mask & ~0xff) != 0 :
        mask = mask >> 1
        shift2+=1
    return shift1, mul, shift2

class QueryDict(dict):
    def __getattr__(self, attr):
        try:
            return self.__getitem__(attr)
        except KeyError:
            try:
                return super(QueryDict, self).__getattr__(attr)
            except AttributeError:
                raise KeyError(attr)

    def __setattr__(self, attr, value):
        self.__setitem__(attr, value)

class DDSException(Exception):
    pass

class Colour8888(object):
    def __init__(self):
        self.red = 0x0
        self.green = 0x0
        self.blue = 0x0
        self.alpha = 0x0

class Colour565(object):
    def __init__(self):
        self.blue = 0x0
        self.green = 0x0
        self.red = 0x0

class DDSFile(object):
    fields = (
        ('size', 0), ('flags', 1), ('height', 2),
        ('width', 3), ('pitchOrLinearSize', 4), ('depth', 5),
        ('mipmapCount', 6), ('pf_size', 18), ('pf_flags', 19),
        ('pf_fourcc', 20), ('pf_rgbBitCount', 21), ('pf_rBitMask', 22),
        ('pf_gBitMask', 23), ('pf_bBitMask', 24), ('pf_aBitMask', 25),
        ('caps1', 26), ('caps2', 27))

    def __init__(self, data):
        super(DDSFile, self).__init__()
        #self._dxt = 0
        self._fmt = None
        self.meta = meta = QueryDict()
        self.count = 0
        self.pixelformat = 'Unknown'
        self.data=data
        self.imagelist={}
        self.colours=[]
        for field, index in DDSFile.fields:
            meta[field] = 0
        if data :
            self.load()

    def getformat(self):
        if (self.meta.pf_flags & DDPF_FOURCC) == DDPF_FOURCC :
            if self.meta.pf_fourcc == DDS_DXT1 :
                self.pixelformat = 'DXT1'
            elif self.meta.pf_fourcc == DDS_DXT2 :
                self.pixelformat = 'DXT2'
            elif self.meta.pf_fourcc == DDS_DXT3 :
                self.pixelformat = 'DXT3'
            elif self.meta.pf_fourcc == DDS_DXT4 :
                self.pixelformat = 'DXT4'
            elif self.meta.pf_fourcc == DDS_DXT5 :
                self.pixelformat = 'DXT5'
            elif self.meta.pf_fourcc == ATI1 :
                self.pixelformat = 'ATI1N'
            elif self.meta.pf_fourcc == ATI2 :
                self.pixelformat = 'THREEDC'
            elif self.meta.pf_fourcc == RXGB :
                self.pixelformat = 'RXGB'
            elif self.meta.pf_fourcc == DOLLARNULL :
                self.pixelformat = 'A16B16G16R16'
            elif self.meta.pf_fourcc == oNULL :
                self.pixelformat = 'R16F'
            elif self.meta.pf_fourcc == pNULL :
                self.pixelformat = 'G16R16F'
            elif self.meta.pf_fourcc == qNULL :
                self.pixelformat = 'A16B16G16R16F'
            elif self.meta.pf_fourcc == rNULL :
                self.pixelformat = 'R32F'
            elif self.meta.pf_fourcc == sNULL :
                self.pixelformat = 'G32R32F'
            elif self.meta.pf_fourcc == tNULL :
                self.pixelformat = 'A32B32G32R32F'
            else :
                raise DDSException('Unsupported FOURCC 0x%08x' % (self.meta.pf_fourcc))
        else :
            if (self.meta.pf_flags & DDPF_LUMINANCE) == DDPF_LUMINANCE :
                if (self.meta.pf_flags & DDPF_ALPHAPIXELS) == DDPF_ALPHAPIXELS :
                    self.pixelformat = 'LUMINANCE_ALPHA'
                else :
                    self.pixelformat = 'LUMINANCE'
            else :
                if (self.meta.pf_flags & DDPF_ALPHAPIXELS) == DDPF_ALPHAPIXELS :
                    self.pixelformat = 'RGBA'
                else :
                    self.pixelformat = 'RGB'

    def getblocksize(self, width, height):
        # int(math.floor ?
        blocksize = int((width + 3) / 4) * int((height + 3) / 4) * self.meta.depth
        if self.pixelformat == 'DXT1' :
            blocksize *= 8
        elif self.pixelformat == 'DXT2' :
            blocksize *= 16
        elif self.pixelformat == 'DXT3' :
            blocksize *= 16
        elif self.pixelformat == 'DXT4' :
            blocksize *= 16
        elif self.pixelformat == 'DXT5' :
            blocksize *= 16
        elif self.pixelformat == 'ATI1N' :
            blocksize *= 8
        elif self.pixelformat == 'THREEDC' :
            blocksize *= 16
        elif self.pixelformat == 'RXGB' :
            blocksize *= 16
        elif self.pixelformat == 'A16B16G16R16' :
            blocksize = width * height * self.meta.depth * 8
        elif self.pixelformat == 'R16F' :
            blocksize = width * height * self.meta.depth * 2
        elif self.pixelformat == 'G16R16F' :
            blocksize = width * height * self.meta.depth * 4
        elif self.pixelformat == 'A16B16G16R16F' :
            blocksize = width * height * self.meta.depth * 8
        elif self.pixelformat == 'R32F' :
            blocksize = width * height * self.meta.depth * 4
        elif self.pixelformat == 'G32R32F' :
            blocksize = width * height * self.meta.depth * 8
        elif self.pixelformat == 'A32B32G32R32F' :
            blocksize = width * height * self.meta.depth * 16
        elif self.pixelformat == 'LUMINANCE_ALPHA' :
            blocksize = width * height * self.meta.depth * (self.meta.pf_rgbBitCount >> 3)
        elif self.pixelformat == 'LUMINANCE' :
            blocksize = width * height * self.meta.depth * (self.meta.pf_rgbBitCount >> 3)
        elif self.pixelformat == 'RGBA' :
            blocksize = width * height * self.meta.depth * (self.meta.pf_rgbBitCount >> 3)
        elif self.pixelformat == 'RGB' :
            blocksize = width * height * self.meta.depth * (self.meta.pf_rgbBitCount >> 3)
        else :
            raise DDSException('Unsupported PixelFormat %s' % (self.pixelformat))
        return blocksize

    def load(self):
        position = 0
        # ensure magic
        if self.data[:4] != b'DDS ':
            raise DDSException('Invalid magic header')
        position += 4

        # read header
        fmt = 'I' * 31
        fmt_size = calcsize(fmt)
        pf_size = calcsize('I' * 8)
        header = self.data[position:position+fmt_size]
        position += fmt_size
        if len(header) != fmt_size:
            raise DDSException('Truncated header in')

        # depack
        header = unpack(fmt, header)
        meta = self.meta
        for name, index in DDSFile.fields:
            meta[name] = header[index]
            if name == "depth" and header[index] == 0 :
                meta.depth = 1

        # check header validity
        if meta.size != fmt_size:
            raise DDSException('Invalid header size (%d instead of %d)' % (meta.size, fmt_size))
        if meta.pf_size != pf_size:
            raise DDSException('Invalid pixelformat size (%d instead of %d)' % (meta.pf_size, pf_size))
        if not check_flags(meta.flags, DDSD_CAPS | DDSD_PIXELFORMAT | DDSD_WIDTH | DDSD_HEIGHT):
            raise DDSException('Not enough flags')
        if not check_flags(meta.caps1, DDSCAPS_TEXTURE):
            raise DDSException('Not a DDS texture')

        self.getformat()
        #size = self.getblocksize(meta.width, meta.height)
        #print("%s %d %d %d" % (self.pixelformat, meta.width, meta.height, size))

        #self.count = 1
        if check_flags(meta.flags, DDSD_MIPMAPCOUNT):
            if not check_flags(meta.caps1, DDSCAPS_COMPLEX | DDSCAPS_MIPMAP):
                if check_flags(meta.caps1, DDSCAPS_TEXTURE) :
                    print("DDSCAPS_TEXTURE")
                raise DDSException('Invalid mipmap without flags 0x%08x' % (meta.caps1))
            #self.count = meta.mipmapCount

        hasrgb = check_flags(meta.pf_flags, DDPF_RGB)
        #hasalpha = check_flags(meta.pf_flags, DDPF_ALPHAPIXELS)
        hasluminance = check_flags(meta.pf_flags, DDPF_LUMINANCE)
        #bpp = None
        #dxt = block = pitch = 0
        #if hasrgb or hasalpha or hasluminance:
        #    bpp = meta.pf_rgbBitCount
        if hasrgb and hasluminance:
            raise DDSException('File have RGB and Luminance')
        #if hasrgb:
        #    dxt = 0
        #elif hasalpha and not hasluminance:
        #    dxt = 1
        #elif hasluminance and not hasalpha:
        #    dxt = 2
        #elif hasalpha and hasluminance:
        #    dxt = 3
        #elif check_flags(meta.pf_flags, DDPF_FOURCC):
        #    dxt = meta.pf_fourcc
        #    if dxt not in (DDS_DXT1, DDS_DXT2, DDS_DXT3, DDS_DXT4, DDS_DXT5):
        #        raise DDSException('Unsupported FOURCC 0x%08x' % (dxt))
        #else:
        #    raise DDSException('Unsupported format specified')
        #if bpp:
        #    block = align_value(bpp, 8) // 8
        #    pitch = align_value(block * meta.width, 4)
        #size = 0
        #if not check_flags(meta.flags, DDSD_LINEARSIZE) :
        #    print('no DDSD_LINEARSIZE') # happens all the time
        #if check_flags(meta.flags, DDSD_LINEARSIZE) :
        #    if dxt in (0, 1, 2, 3) :
        #        size = pitch * meta.height
        #    else:
        #        size = dxt_size(meta.width, meta.height, dxt)
        datal = len(self.data)
        w = meta.width
        h = meta.height
        i=0
        while position<datal :
            #if dxt in (0, 1, 2, 3) :
            #    size = align_value(block * w, 4) * h
            #else:
            #    size = dxt_size(w, h, dxt)
            size = self.getblocksize(w, h)
            if position + size > datal :
                raise DDSException('Truncated image for mipmap %d at %d +size %d > %d total size' % (i, position, size, datal))
            self.imagelist[i]={}
            self.imagelist[i]["width"]=w
            self.imagelist[i]["height"]=h
            self.imagelist[i]["position"]=position
            self.imagelist[i]["size"]=size
            position += size
            if w == 1 and h == 1 :
                break
            w = max(1, w // 2)
            h = max(1, h // 2)
            i+=1
        self.count = len(self.imagelist)
        if position!=datal :
            raise DDSException("total size mismatch %4d != %4d" % (position, datal))
        #self._dxt = dxt

    def stripbiggermipmapthan(self, sizelimit):
        choice = -1
        for i in range(self.count) :
            if self.imagelist[i]["width"]<=sizelimit and self.imagelist[i]["height"]<=sizelimit :
                choice = i
                break
        if choice == -1 :
            raise DDSException("no smaller mipmap found")
        newwidth = (self.imagelist[choice]["width"]).to_bytes(4, byteorder='little', signed=True)
        newheight = (self.imagelist[choice]["height"]).to_bytes(4, byteorder='little', signed=True)
        newmipmapcount = (self.count - choice).to_bytes(4, byteorder='little', signed=True)
        return self.data[:12] + newheight + newwidth + self.data[20:28] + newmipmapcount + self.data[32:128] + self.data[self.imagelist[choice]["position"]:]

    def stripratiomipmap(self, divideby):
        choice = -1
        widthlimit = int(self.meta.width/divideby)
        heightlimit = int(self.meta.height/divideby)
        for i in range(self.count) :
            if self.imagelist[i]["width"]<=widthlimit and self.imagelist[i]["height"]<=heightlimit :
                choice = i
                break
        if choice == -1 :
            raise DDSException("no smaller mipmap found")
        newwidth = (self.imagelist[choice]["width"]).to_bytes(4, byteorder='little', signed=True)
        newheight = (self.imagelist[choice]["height"]).to_bytes(4, byteorder='little', signed=True)
        newmipmapcount = (self.count - choice).to_bytes(4, byteorder='little', signed=True)
        return self.data[:12] + newheight + newwidth + self.data[20:28] + newmipmapcount + self.data[32:128] + self.data[self.imagelist[choice]["position"]:]

    def decode(self, thisimage) :
        width = self.imagelist[thisimage]["width"]
        height = self.imagelist[thisimage]["height"]
        pos = self.imagelist[thisimage]["position"]
        if self.pixelformat == 'DXT1' :
            return self.DecompressDXT1(width, height, pos)
        elif self.pixelformat == 'DXT2' :
            return self.DecompressDXT3(width, height, pos, False)
        elif self.pixelformat == 'DXT3' :
            return self.DecompressDXT3(width, height, pos, False)
        elif self.pixelformat == 'DXT4' :
            return self.DecompressDXT5(width, height, pos, False)
        elif self.pixelformat == 'DXT5' :
            return self.DecompressDXT5(width, height, pos, False)
        elif self.pixelformat == 'RGBA' :
            return self.DecompressRGBA(width, height, pos)
        else :
            raise DDSException("Cannot decode format %s" % (self.pixelformat))

    def DxtcReadColor(self, myshort, indexe) :
        b = (myshort & 0x1f)
        g = (myshort & 0x7E0) >> 5
        r = (myshort & 0xF800) >> 11
        self.colours[indexe].red   = 0xff & (r << 3 | r >> 2)
        self.colours[indexe].green = 0xff & (g << 2 | g >> 3)
        self.colours[indexe].blue  = 0xff & (b << 3 | r >> 2)

    def DecompressDXT1(self, width, height, pos):
        bpp = PixelFormatToBpp(self.pixelformat, self.meta.pf_rgbBitCount)
        bps = width * bpp * PixelFormatToBpc(self.pixelformat)
        sizeofplane = bps * height
        rawData = bytearray(self.meta.depth * sizeofplane + height * bps + width * bpp)
        self.colours.clear()
        self.colours = [Colour8888(), Colour8888(), Colour8888(), Colour8888()]
        self.colours[0].alpha = 0xFF
        self.colours[1].alpha = 0xFF
        self.colours[2].alpha = 0xFF
        #maxwidth = 0
        #maxheight = 0
        for z in range(self.meta.depth) :
            for y in range(0, height, 4) :
                for x in range(0, width, 4) :
                    colour0 = (self.data[pos+1] << 8) | self.data[pos]
                    pos+=2
                    colour1 = (self.data[pos+1] << 8) | self.data[pos]
                    pos+=2
                    bitmask = (self.data[pos+3] << 24) | (self.data[pos+2] << 16) | (self.data[pos+1] << 8) | (self.data[pos])
                    pos+=4
                    self.DxtcReadColor(colour0, 0)
                    self.DxtcReadColor(colour1, 1)
                    if (colour0 > colour1) :
                        # Four-color block: derive the other two colors.
                        # 00 = color_0, 01 = color_1, 10 = color_2, 11 = color_3
                        # These 2-bit codes correspond to the 2-bit fields
                        # stored in the 64-bit block.
                        self.colours[2].blue = int((2 * self.colours[0].blue + self.colours[1].blue + 1) / 3)
                        self.colours[2].green = int((2 * self.colours[0].green + self.colours[1].green + 1) / 3)
                        self.colours[2].red = int((2 * self.colours[0].red + self.colours[1].red + 1) / 3)
                        #self.colours[2].alpha = 0xFF
                        self.colours[3].blue = int((self.colours[0].blue + 2 * self.colours[1].blue + 1) / 3)
                        self.colours[3].green = int((self.colours[0].green + 2 * self.colours[1].green + 1) / 3)
                        self.colours[3].red = int((self.colours[0].red + 2 * self.colours[1].red + 1) / 3)
                        self.colours[3].alpha = 0xFF
                    else :
                        # Three-color block: derive the other color.
                        # 00 = color_0,  01 = color_1,  10 = color_2,
                        # 11 = transparent.
                        # These 2-bit codes correspond to the 2-bit fields
                        # stored in the 64-bit block.
                        self.colours[2].blue = int((self.colours[0].blue + self.colours[1].blue) / 2)
                        self.colours[2].green = int((self.colours[0].green + self.colours[1].green) / 2)
                        self.colours[2].red = int((self.colours[0].red + self.colours[1].red) / 2)
                        #self.colours[2].alpha = 0xFF
                        self.colours[3].blue = int((self.colours[0].blue + 2 * self.colours[1].blue + 1) / 3)
                        self.colours[3].green = int((self.colours[0].green + 2 * self.colours[1].green + 1) / 3)
                        self.colours[3].red = int((self.colours[0].red + 2 * self.colours[1].red + 1) / 3)
                        self.colours[3].alpha = 0x00
                    k = 0
                    for j in range(4) :
                        for i in range(4) :
                            select = (bitmask & (0x03 << k * 2)) >> k * 2
                            if (((x + i) < width) and ((y + j) < height)) :
                                offset = z * sizeofplane + (y + j) * bps + (x + i) * bpp
                                #if x + i > maxwidth :
                                #    maxwidth = x + i
                                #if y + j > maxheight :
                                #    maxheight = y + j
                                rawData[offset + 0] = self.colours[select].red
                                rawData[offset + 1] = self.colours[select].green
                                rawData[offset + 2] = self.colours[select].blue
                                rawData[offset + 3] = self.colours[select].alpha
                            k+=1
        return rawData

    def DxtcReadColors(self, data) :
        b0 = (data[0] & 0x1F)
        g0 = (((data[0] & 0xE0) >> 5) | ((data[1] & 0x7) << 3))
        r0 = ((data[1] & 0xF8) >> 3)
        b1 = (data[2] & 0x1F)
        g1 = (((data[2] & 0xE0) >> 5) | ((data[3] & 0x7) << 3))
        r1 = ((data[3] & 0xF8) >> 3)
        self.colours[0].red   = 0xff & (r0 << 3 | r0 >> 2)
        self.colours[0].green = 0xff & (g0 << 2 | g0 >> 3)
        self.colours[0].blue  = 0xff & (b0 << 3 | b0 >> 2)
        self.colours[1].red   = 0xff & (r1 << 3 | r1 >> 2)
        self.colours[1].green = 0xff & (g1 << 2 | g1 >> 3)
        self.colours[1].blue  = 0xff & (b1 << 3 | b1 >> 2)

    def CorrectPremult(self, pixnum, buffer) :
        for i in range(0, pixnum*4, 4) :
            alpha = buffer[i + 3]
            if (alpha == 0) :
                continue
            red   = int((buffer[i    ] * 255) / alpha)
            green = int((buffer[i + 1] * 255) / alpha)
            blue  = int((buffer[i + 2] * 255) / alpha)
            buffer[i]     = 0xff & red
            buffer[i + 1] = 0xff & green
            buffer[i + 2] = 0xff & blue
        return buffer

    def DecompressDXT2(self, width, height, pos):
        # Can do color & alpha same as dxt3, but color is pre-multiplied
        # so the result will be wrong unless corrected.
        rawData = self.DecompressDXT3(width, height, pos, False)
        return self.CorrectPremult((width * height * self.meta.depth), rawData)

    def DecompressDXT4(self, width, height, pos):
        # Can do color & alpha same as dxt5, but color is pre-multiplied
        # so the result will be wrong unless corrected.
        rawData = self.DecompressDXT5(width, height, pos)
        return self.CorrectPremult((width * height * self.meta.depth), rawData)

    def DecompressDXT3(self, width, height, pos, premultiplied):
        bpp = PixelFormatToBpp(self.pixelformat, self.meta.pf_rgbBitCount)
        bps = width * bpp * PixelFormatToBpc(self.pixelformat)
        sizeofplane = bps * height
        rawData = bytearray(self.meta.depth * sizeofplane + height * bps + width * bpp)
        self.colours.clear()
        self.colours = [Colour8888(), Colour8888(), Colour8888(), Colour8888()]
        for z in range(self.meta.depth) :
            for y in range(0, height, 4) :
                for x in range(0, width, 4) :
                    alpha = self.data[pos:pos+8]
                    pos+=8
                    self.DxtcReadColors(self.data[pos:pos+4])
                    pos+=4
                    bitmask = (self.data[pos+3] << 24) | (self.data[pos+2] << 16) | (self.data[pos+1] << 8) | (self.data[pos])
                    pos+=4
                    # Four-color block: derive the other two colors.
                    # 00 = color_0, 01 = color_1, 10 = color_2, 11 = color_3
                    # These 2-bit codes correspond to the 2-bit fields
                    # stored in the 64-bit block.
                    self.colours[2].blue  = int((2 * self.colours[0].blue + self.colours[1].blue + 1) / 3)
                    self.colours[2].green = int((2 * self.colours[0].green + self.colours[1].green + 1) / 3)
                    self.colours[2].red  = int((2 * self.colours[0].red + self.colours[1].red + 1) / 3)
                    #self.colours[2].alpha = 0xFF
                    self.colours[3].blue  = int((self.colours[0].blue + 2 * self.colours[1].blue + 1) / 3)
                    self.colours[3].green = int((self.colours[0].green + 2 * self.colours[1].green + 1) / 3)
                    self.colours[3].red  = int((self.colours[0].red + 2 * self.colours[1].red + 1) / 3)
                    #self.colours[3].alpha = 0xFF
                    k = 0
                    for j in range(4) :
                        for i in range(4) :
                            select = (bitmask & (0x03 << k * 2)) >> k * 2
                            if (((x + i) < width) and ((y + j) < height)) :
                                offset = z * sizeofplane + (y + j) * bps + (x + i) * bpp
                                rawData[offset + 0] = self.colours[select].red
                                rawData[offset + 1] = self.colours[select].green
                                rawData[offset + 2] = self.colours[select].blue
                            k+=1
                    for j in range(4) :
                        # ushort word = (ushort)(alpha[2 * j] + 256 * alpha[2 * j + 1]);
                        word = (alpha[2 * j] | (alpha[2 * j + 1] << 8))
                        for i in range(4) :
                            if (((x + i) < width) and ((y + j) < height)) :
                                offset = z * sizeofplane + (y + j) * bps + (x + i) * bpp + 3
                                rawData[offset] = word & 0x0F
                                rawData[offset] = 0xff & (rawData[offset] | (rawData[offset] << 4))
                                if premultiplied is True :
                                    if rawData[offset] != 0 :
                                        rawData[offset - 3] = 0xff & int((rawData[offset - 3] * 0xff) / rawData[offset])
                                        rawData[offset - 2] = 0xff & int((rawData[offset - 2] * 0xff) / rawData[offset])
                                        rawData[offset - 1] = 0xff & int((rawData[offset - 1] * 0xff) / rawData[offset])
                            word = word >> 4
        return rawData

    def DecompressDXT5(self, width, height, pos, premultiplied):
        bpp = PixelFormatToBpp(self.pixelformat, self.meta.pf_rgbBitCount)
        bps = width * bpp * PixelFormatToBpc(self.pixelformat)
        sizeofplane = bps * height
        rawData = bytearray(self.meta.depth * sizeofplane + height * bps + width * bpp)
        self.colours.clear()
        self.colours = [Colour8888(), Colour8888(), Colour8888(), Colour8888()]
        alphas = [0, 0, 0, 0, 0, 0, 0, 0]
        for z in range(self.meta.depth) :
            for y in range(0, height, 4) :
                for x in range(0, width, 4) :
                    alphas[0] = self.data[pos]
                    pos+=1
                    alphas[1] = self.data[pos]
                    pos+=1
                    alphamask = self.data[pos:pos+6]
                    pos+=6
                    self.DxtcReadColors(self.data[pos:pos+4])
                    pos+=4
                    bitmask = (self.data[pos+3] << 24) | (self.data[pos+2] << 16) | (self.data[pos+1] << 8) | (self.data[pos])
                    pos+=4
                    # Four-color block: derive the other two colors.
                    # 00 = color_0, 01 = color_1, 10 = color_2, 11 = color_3
                    # These 2-bit codes correspond to the 2-bit fields
                    # stored in the 64-bit block.
                    self.colours[2].blue = int((2 * self.colours[0].blue + self.colours[1].blue + 1) / 3)
                    self.colours[2].green = int((2 * self.colours[0].green + self.colours[1].green + 1) / 3)
                    self.colours[2].red = int((2 * self.colours[0].red + self.colours[1].red + 1) / 3)
                    #self.colours[2].alpha = 0xFF
                    self.colours[3].blue = int((self.colours[0].blue + 2 * self.colours[1].blue + 1) / 3)
                    self.colours[3].green = int((self.colours[0].green + 2 * self.colours[1].green + 1) / 3)
                    self.colours[3].red = int((self.colours[0].red + 2 * self.colours[1].red + 1) / 3)
                    #self.colours[3].alpha = 0xFF
                    k = 0
                    for j in range(4) :
                        for i in range(4) :
                            select = (bitmask & (0x03 << k * 2)) >> k * 2
                            if (((x + i) < width) and ((y + j) < height)) :
                                offset = z * sizeofplane + (y + j) * bps + (x + i) * bpp
                                rawData[offset + 0] = self.colours[select].red
                                rawData[offset + 1] = self.colours[select].green
                                rawData[offset + 2] = self.colours[select].blue
                            k+=1
                    # 8-alpha or 6-alpha block?
                    if (alphas[0] > alphas[1]) :
                        # 8-alpha block:  derive the other six alphas.
                        # Bit code 000 = alpha_0, 001 = alpha_1, others are interpolated.
                        alphas[2] = int(math.floor((6 * alphas[0] + 1 * alphas[1] + 3) / 7)) # bit code 010
                        alphas[3] = int(math.floor((5 * alphas[0] + 2 * alphas[1] + 3) / 7)) # bit code 011
                        alphas[4] = int(math.floor((4 * alphas[0] + 3 * alphas[1] + 3) / 7)) # bit code 100
                        alphas[5] = int(math.floor((3 * alphas[0] + 4 * alphas[1] + 3) / 7)) # bit code 101
                        alphas[6] = int(math.floor((2 * alphas[0] + 5 * alphas[1] + 3) / 7)) # bit code 110
                        alphas[7] = int(math.floor((1 * alphas[0] + 6 * alphas[1] + 3) / 7)) # bit code 111
                    else :
                        # 6-alpha block.
                        # Bit code 000 = alpha_0, 001 = alpha_1, others are interpolated.
                        alphas[2] = int(math.floor((4 * alphas[0] + 1 * alphas[1] + 2) / 5)) # Bit code 010
                        alphas[3] = int(math.floor((3 * alphas[0] + 2 * alphas[1] + 2) / 5)) # Bit code 011
                        alphas[4] = int(math.floor((2 * alphas[0] + 3 * alphas[1] + 2) / 5)) # Bit code 100
                        alphas[5] = int(math.floor((1 * alphas[0] + 4 * alphas[1] + 2) / 5)) # Bit code 101
                        alphas[6] = 0x00 # Bit code 110
                        alphas[7] = 0xFF # Bit code 111
                    # Note: Have to separate the next two loops,
                    # it operates on a 6-byte system.
                    # First three bytes
                    # uint bits = (uint)(alphamask[0]);
                    bits = ((alphamask[0]) | (alphamask[1] << 8) | (alphamask[2] << 16))
                    for j in range(2) :
                        for i in range(4) :
                            if (((x + i) < width) and ((y + j) < height)) :
                                offset = z * sizeofplane + (y + j) * bps + (x + i) * bpp + 3
                                rawData[offset] = alphas[bits & 0x07]
                                if premultiplied is True :
                                    if rawData[offset] != 0 :
                                        rawData[offset - 3] = 0xff & int((rawData[offset - 3] * 0xff) / rawData[offset])
                                        rawData[offset - 2] = 0xff & int((rawData[offset - 2] * 0xff) / rawData[offset])
                                        rawData[offset - 1] = 0xff & int((rawData[offset - 1] * 0xff) / rawData[offset])
                            bits = bits >> 3
                    # Last three bytes
                    # uint bits = (uint)(alphamask[3]);
                    bits = ((alphamask[3]) | (alphamask[4] << 8) | (alphamask[5] << 16))
                    for j in range(2, 4) :
                        for i in range(4) :
                            if (((x + i) < width) and ((y + j) < height)) :
                                offset = z * sizeofplane + (y + j) * bps + (x + i) * bpp + 3
                                rawData[offset] = alphas[bits & 0x07]
                                if premultiplied is True :
                                    if rawData[offset] != 0 :
                                        rawData[offset - 3] = 0xff & int((rawData[offset - 3] * 0xff) / rawData[offset])
                                        rawData[offset - 2] = 0xff & int((rawData[offset - 2] * 0xff) / rawData[offset])
                                        rawData[offset - 1] = 0xff & int((rawData[offset - 1] * 0xff) / rawData[offset])
                            bits = bits >> 3
        return rawData

    def DecompressRGBA(self, width, height, pos):
        bpp = PixelFormatToBpp(self.pixelformat, self.meta.pf_rgbBitCount)
        bps = width * bpp * PixelFormatToBpc(self.pixelformat)
        sizeofplane = bps * height
        rawData = bytearray(self.meta.depth * sizeofplane + height * bps + width * bpp)
        if self.meta.pf_rgbBitCount == 32 :
            valMask = ~0 #-1
        else :
            valMask = 1 << int(self.meta.pf_rgbBitCount) - 1
        # Funny x86s, make 1 << 32 == 1
        pixSize = int((self.meta.pf_rgbBitCount + 7) / 8)
        rShift1, rMul, rShift2 = ComputeMaskParams(self.meta.pf_rBitMask)
        gShift1, gMul, gShift2 = ComputeMaskParams(self.meta.pf_gBitMask)
        bShift1, bMul, bShift2 = ComputeMaskParams(self.meta.pf_bBitMask)
        aShift1, aMul, aShift2 = ComputeMaskParams(self.meta.pf_aBitMask)
        offset = 0
        pixnum = width * height * self.meta.depth
        while (pixnum > 0) :
            mydata = (self.data[pos+3] << 24) | (self.data[pos+2] << 16) | (self.data[pos+1] << 8) | (self.data[pos])
            px = mydata & valMask
            pos += pixSize
            pxc = px & self.meta.pf_rBitMask
            rawData[offset + 0] = 0xff & (((pxc >> rShift1) * rMul) >> rShift2)
            pxc = px & self.meta.pf_gBitMask
            rawData[offset + 1] = 0xff & (((pxc >> gShift1) * gMul) >> gShift2)
            pxc = px & self.meta.pf_gBitMask
            rawData[offset + 2] = 0xff & (((pxc >> bShift1) * bMul) >> bShift2)
            pxc = px & self.meta.pf_aBitMask
            rawData[offset + 3] = 0xff & (((pxc >> aShift1) * aMul) >> aShift2)
            offset += 4
            pixnum-=1
        return rawData

    def save(self, filename):
        if len(self.images) == 0:
            raise DDSException('No images to save')

        fields = dict(DDSFile.fields)
        fields_keys = list(fields.keys())
        fields_index = list(fields.values())
        mget = self.meta.get
        header = []
        for idx in range(31):
            if idx in fields_index:
                value = mget(fields_keys[fields_index.index(idx)], 0)
            else:
                value = 0
            header.append(value)

        with open(filename, 'wb') as fd:
            fd.write('DDS ')
            fd.write(pack('I' * 31, *header))
            for image in self.images:
                fd.write(image)

    def add_image(self, level, bpp, fmt, width, height, data):
        assert(bpp == 32)
        assert(fmt in ('rgb', 'rgba', 'dxt1', 'dxt2', 'dxt3', 'dxt4', 'dxt5'))
        assert(width > 0)
        assert(height > 0)
        assert(level >= 0)

        meta = self.meta
        images = self.images
        if len(images) == 0:
            assert(level == 0)

            # first image, set defaults !
            for k in meta.keys():
                meta[k] = 0

            self._fmt = fmt
            meta.size = calcsize('I' * 31)
            meta.pf_size = calcsize('I' * 8)
            meta.pf_flags = 0
            meta.flags = DDSD_CAPS | DDSD_PIXELFORMAT | DDSD_WIDTH | DDSD_HEIGHT
            meta.width = width
            meta.height = height
            meta.caps1 = DDSCAPS_TEXTURE

            meta.flags |= DDSD_LINEARSIZE
            meta.pitchOrLinearSize = len(data)

            meta.pf_rgbBitCount = 32
            meta.pf_rBitMask = 0x00ff0000
            meta.pf_gBitMask = 0x0000ff00
            meta.pf_bBitMask = 0x000000ff
            meta.pf_aBitMask = 0xff000000

            if fmt in ('rgb', 'rgba'):
                assert(True)
                assert(bpp == 32)
                meta.pf_flags |= DDPF_RGB
                meta.pf_rgbBitCount = 32
                meta.pf_rBitMask = 0x00ff0000
                meta.pf_gBitMask = 0x0000ff00
                meta.pf_bBitMask = 0x000000ff
                meta.pf_aBitMask = 0x00000000
                if fmt == 'rgba':
                    meta.pf_flags |= DDPF_ALPHAPIXELS
                    meta.pf_aBitMask = 0xff000000
            else:
                meta.pf_flags |= DDPF_FOURCC
                if fmt == 'dxt1':
                    meta.pf_fourcc = DDS_DXT1
                elif fmt == 'dxt2':
                    meta.pf_fourcc = DDS_DXT2
                elif fmt == 'dxt3':
                    meta.pf_fourcc = DDS_DXT3
                elif fmt == 'dxt4':
                    meta.pf_fourcc = DDS_DXT4
                elif fmt == 'dxt5':
                    meta.pf_fourcc = DDS_DXT5

            images.append(data)
        else:
            assert(level == len(images))
            assert(fmt == self._fmt)

            images.append(data)

            meta.flags |= DDSD_MIPMAPCOUNT
            meta.caps1 |= DDSCAPS_COMPLEX | DDSCAPS_MIPMAP
            meta.mipmapCount = len(images)

    def __repr__(self):
        return '<DDSFile size=%r dxt=%r width=%r height=%r mipmapCount=%r>' % (self.size, self.dxt, self.width, self.height, self.mipmapCount)

    def _get_size(self):
        meta = self.meta
        return meta.width, meta.height
    def _set_size(self, size):
        self.meta.update({'width': size[0], 'height': size[1]})
    size = property(_get_size, _set_size)

    def _get_width(self):
        meta = self.meta
        return meta.width
    def _set_width(self, width):
        self.meta.update({'width': width})
    width = property(_get_width, _set_width)

    def _get_height(self):
        meta = self.meta
        return meta.height
    def _set_height(self, height):
        self.meta.update({'height': height})
    height = property(_get_height, _set_height)

    def _get_mipmapCount(self):
        meta = self.meta
        return meta.mipmapCount
    def _set_mipmapCount(self, mipmapCount):
        self.meta.update({'mipmapCount': mipmapCount})
    mipmapCount = property(_get_mipmapCount, _set_mipmapCount)

    def _get_dxt(self):
        return self.pixelformat
    def _set_dxt(self, dxt):
        self.pixelformat = dxt
    dxt = property(_get_dxt, _set_dxt)




