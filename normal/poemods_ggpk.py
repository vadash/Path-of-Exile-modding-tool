#!/usr/bin/python3
import binascii
import datetime
import sys
import time
import re
import os
import codecs
import copy
import shutil
import hashlib

class listggpkfiles(object):
    def __init__(self):
        self.ggpkname=None
        self.ggpksize=0
        self.ggpkhash="ghkf"
        self.fullfilelist=[]
        self.fullfilelistdic={}
        self.refdic={}
        self.firstfreerecord=-1
        self.ggpknameinfo=None
        self.keeplist={}
        if os.path.exists("keep") is False :
            os.makedirs("keep")
        self.keeplistf=os.path.join("keep", "keeplist.dat")
        self.isthemod=False
        self.forcescan=False

    def rescanggpk(self, ggpkname, forcerescan, isthemod):
        self.forcescan=forcerescan
        self.isthemod=isthemod
        self.ggpkname=None
        self.ggpksize=0
        self.ggpkhash="ghkf"
        self.fullfilelist.clear()
        self.fullfilelistdic.clear()
        self.refdic.clear()
        self.firstfreerecord=-1
        self.ggpknameinfo=None
        if os.path.exists(ggpkname) is False :
            self.ggpkname=None
            print("path does not exist : "+ggpkname)
            return None
        self.ggpkname=ggpkname
        ggpknameinfo=ggpkname.replace('/', '')
        ggpknameinfo=ggpknameinfo.replace('\\', '')
        ggpknameinfo=ggpknameinfo.replace(':', '')
        ggpknameinfo=ggpknameinfo.replace(' ', '')
        ggpknameinfo=ggpknameinfo.replace('.', '')
        ggpknameinfo+=".txt"
        self.fullfilelist.clear()
        self.fullfilelistdic.clear()
        self.refdic.clear()
        self.ggpkhash="ghkf"
        self.firstfreerecord=-1
        self.ggpknameinfo=os.path.join("keep", ggpknameinfo)
        self.ggpksize=os.path.getsize(ggpkname)
        if self.ggpksize<100 :
            self.ggpkname=None
            print("error ggpk size %d" % (self.ggpksize))
            return None
        if self.isthemod is True :
            self.keeplist.clear()
            if os.path.exists(self.keeplistf) is False :
                with open(self.keeplistf, "w") as fout :
                    fout.write("")
            else :
                ligne=0
                with open(self.keeplistf, "r") as fin :
                    for line in fin :
                        if len(line)>0 :
                            if line[-1]=='\n' :
                                line=line[:-1]
                        data=line.split('\t')
                        if len(data)==2 :
                            self.keeplist[data[0]]=data[1]
        self.gethash()
        rescan=True
        if os.path.exists(self.ggpknameinfo) is True and forcerescan is False :
            firstline=True
            with open(self.ggpknameinfo, "r", encoding="UTF-8") as fin :
                for line in fin :
                    if len(line)>0 :
                        if line[-1]=='\n' :
                            line=line[:-1]
                    data=line.split('\t')
                    if len(data)==5 :
                        path=data[0]
                        name=data[1]
                        filename=path+name
                        self.fullfilelist.append(filename)
                        self.fullfilelistdic[filename]={
                            "path" : path,
                            "name" : name,
                            "position" : int(data[2]),
                            "length" : int(data[3]),
                            "referenceposition" : int(data[4])
                            }
                    elif len(line)>0 :
                        if firstline is True :
                            firstline=False
                            if line==self.ggpkhash :
                                rescan=False
                            else :
                                print("hash different : rescan needed")
                                break
                        else :
                            self.firstfreerecord=int(line)
        if rescan is True :
            with open(self.ggpkname, "rb") as ggpk :
                record_length = int.from_bytes(ggpk.read(4), byteorder='little', signed=False)
                tag = ggpk.read(4).decode("UTF-8")
                if tag != "GGPK":
                    print("not a valid GGPK given")
                    self.ggpkname=None
                    return None
                child_count = int.from_bytes(ggpk.read(4), byteorder='little', signed=False)
                headerlength = 4 + 4 + 4
                children = []
                for i in range(child_count):
                    pos=ggpk.tell()
                    absolute_offset = int.from_bytes(ggpk.read(8), byteorder='little', signed=False)
                    self.refdic[absolute_offset]=pos
                    children.append(absolute_offset)
                filename="."
                self.fullfilelist.append(filename)
                self.fullfilelistdic[filename]={
                    "position" : 0,
                    "length" : record_length,
                    "path" : "",
                    "name" : ".",
                    "referenceposition" : 0
                    }
                print("%12d %6d %s " % (self.fullfilelistdic[filename]["position"], self.fullfilelistdic[filename]["length"], filename) + str(children))
                self.traverse_children(".", children, ggpk)
                print("unused should be none : ", end="")
                print(self.refdic)
            self.fullfilelist.sort(key=str.lower)
            self.saveinfo()

    def traverse_children(self, path, children, ggpk):
        for absoluteposition in children:
            ggpk.seek(absoluteposition)
            # maximum 4+4+4+4+32+150*2+12*1437 = 17952
            buffer = ggpk.read(81920)
            bi = 0
            bf = bi+4
            record_length = int.from_bytes(buffer[bi:bf], byteorder='little', signed=False)
            bi = bf
            bf = bi+4
            tag = buffer[bi:bf].decode("UTF-8")
            if tag == "PDIR":
                bi = bf
                bf = bi+4
                name_length = int.from_bytes(buffer[bi:bf], byteorder='little', signed=False)
                bi = bf
                bf = bi+4
                child_count = int.from_bytes(buffer[bi:bf], byteorder='little', signed=False)
                bi = bf
                bf = bi+32
                # digest = buffer[bi:bf]
                bi = bf
                bf = bi+name_length * 2
                name = buffer[bi:bf].decode("UTF-16LE")[:-1]
                headerlength = bf
                children = []
                for i in range(child_count):
                    bi = bf
                    bf = bi+4
                    #timestamp = int.from_bytes(buffer[bi:bf], byteorder='little', signed=False)
                    bi = bf
                    bf = bi+8
                    absolute_offset = int.from_bytes(buffer[bi:bf], byteorder='little', signed=False)
                    self.refdic[absolute_offset]=absoluteposition+4+4+4+4+32+name_length*2+12*i+4
                    children.append(absolute_offset)
                self.fullfilelist.append(path+name+"/")
                self.fullfilelistdic[path+name+"/"]={
                    "position" : absoluteposition,
                    "length" : record_length,
                    "path" : path,
                    "name" : name+"/",
                    "referenceposition" : self.refdic[absoluteposition]
                    }
                self.refdic.pop(absoluteposition)
                self.traverse_children(path+name+"/", children, ggpk)
            elif tag == "FILE":
                bi = bf
                bf = bi+4
                name_length = int.from_bytes(buffer[bi:bf], byteorder='little', signed=False)
                bi = bf
                bf = bi+32
                # digest = buffer[bi:bf]
                bi = bf
                bf = bi+name_length * 2
                name = buffer[bi:bf].decode("UTF-16LE")[:-1]
                headerlength = bf
                self.fullfilelist.append(path+name)
                self.fullfilelistdic[path+name]={
                    "position" : absoluteposition,
                    "length" : record_length,
                    "path" : path,
                    "name" : name,
                    "referenceposition" : self.refdic[absoluteposition]
                    }
                self.refdic.pop(absoluteposition)
            elif tag == "FREE":
                bi = bf
                bf = bi+8
                next_record = int.from_bytes(buffer[bi:bf], byteorder='little', signed=False)
                if self.firstfreerecord==-1 :
                    print("%12d %6d (%4d) %s first free record -> %d" % (absoluteposition, record_length, 8, path, next_record))
                    self.firstfreerecord=self.refdic[absoluteposition]
                    self.refdic.pop(absoluteposition)
            else:
                print("new tag " + tag)

    def gethash(self):
        ggpksize=self.ggpksize
        hashstart=""
        hashend=""
        hashlength=50000000
        with open(self.ggpkname, "rb") as fin :
            fin.seek(0)
            ggpkpart=fin.read(hashlength)
            hashstart=hashlib.sha256(ggpkpart).hexdigest()
            fin.seek(ggpksize-hashlength)
            ggpkpart=fin.read(hashlength)
            hashend=hashlib.sha256(ggpkpart).hexdigest()
        self.ggpkhash=hashstart+hashend+str(ggpksize)

    def saveinfo(self):
        self.gethash()
        if self.isthemod is True :
            with open(self.keeplistf, "w") as fout :
                for filename in self.keeplist :
                    fout.write("%s\t%s\n" % (filename, self.keeplist[filename]))
        with open(self.ggpknameinfo, "w") as fout :
            fout.write("%s\n" % (self.ggpkhash))
            fout.write("%d\n" % (self.firstfreerecord))
            for filename in self.fullfilelist :
                if filename in self.fullfilelistdic :
                    fout.write("%s\t%s\t%d\t%d\t%d\n" % (self.fullfilelistdic[filename]["path"], self.fullfilelistdic[filename]["name"], self.fullfilelistdic[filename]["position"], self.fullfilelistdic[filename]["length"], self.fullfilelistdic[filename]["referenceposition"]))

    def defragment(self, defragmentto):
        #if self.forcescan is False :
        #    self.rescanggpk(self.ggpkname, True, True)
        fullfilelist2dic={}
        fullfilelist2dic["."]=copy.copy(self.fullfilelistdic["."])
        directory = os.path.dirname(defragmentto)
        if os.path.exists(directory) is False :
            os.makedirs(directory)
        pos=0
        with open(defragmentto, "wb") as ggpkout :
            with open(self.ggpkname, "rb") as ggpk :
                ggpk.seek(self.fullfilelistdic["."]["position"])
                data=ggpk.read(self.fullfilelistdic["."]["length"])
                ggpkout.write(data)
                pos+=self.fullfilelistdic["."]["length"]
                for name in self.fullfilelist :
                    if name=="." :
                        continue
                    ggpk.seek(self.fullfilelistdic[name]["position"])
                    data=ggpk.read(self.fullfilelistdic[name]["length"])
                    ggpkout.write(data)
                    fullfilelist2dic[name]=copy.copy(self.fullfilelistdic[name])
                    fullfilelist2dic[name]["position"]=pos
                    path=self.fullfilelistdic[name]["path"]
                    newrefpos=self.fullfilelistdic[name]["referenceposition"]-self.fullfilelistdic[path]["position"]+fullfilelist2dic[path]["position"]
                    fullfilelist2dic[name]["referenceposition"]=newrefpos
                    ggpkout.seek(newrefpos)
                    writenewaddress=(pos).to_bytes(8, byteorder='little', signed=False)
                    ggpkout.write(writenewaddress)
                    pos+=self.fullfilelistdic[name]["length"]
                    ggpkout.seek(pos)
            if self.firstfreerecord!=-1 :
                writenewaddress=(pos).to_bytes(8, byteorder='little', signed=False)
                # 00000016FREE00000000
                ggpkout.write(b'\x10\x00\x00\x00\x46\x52\x45\x45\x00\x00\x00\x00\x00\x00\x00\x00')
                ggpkout.seek(self.firstfreerecord)
                ggpkout.write(writenewaddress)
        #self.fullfilelistdic.clear()
        #self.fullfilelistdic=copy.deepcopy(fullfilelist2dic)
        #self.ggpksize=os.path.getsize(self.ggpkname)
        #self.saveinfo()

    def stringcleanup(self, piece, encoding):
        bom=b''
        if piece is not None :
            piecel=len(piece)
            if piecel>=2 :
                if piece[0:2]==b'\xff\xfe' :
                    bom=b'\xff\xfe'
                    encoding="UTF-16-LE"
                elif piece[0:2]==b'\xfe\xff' :
                    bom=b'\xfe\xff'
                    encoding="UTF-16-BE"
            if piecel>=3 :
                if piece[0:2]==b'\xef\xbb\xbf' :
                    bom=b'\xef\xbb\xbf'
                    encoding="UTF-8"
            if encoding=="UTF-8" :
                strong=""
                for i in range(piecel) :
                    if piece[i]==0x9 or piece[i]==0xa or piece[i]==0xd or (0x20<=piece[i] and piece[i]<=0x7e) :
                        strong+="%c" % piece[i]
                return strong, encoding, bom
            elif encoding=="UTF-16-LE" :
                piecel-=1
                strong=""
                for i in range(piecel) :
                    paire=i%2
                    if paire==0 :
                        if piece[i+1]==0x0 :
                            if piece[i]==0x9 or piece[i]==0xa or piece[i]==0xd or (0x20<=piece[i] and piece[i]<=0x7e) :
                                strong+="%c" % piece[i]
                return strong, encoding, bom
            elif encoding=="UTF-16-BE" :
                piecel-=1
                strong=""
                for i in range(piecel) :
                    paire=i%2
                    if paire==1 :
                        if piece[i-1]==0x0 :
                            if piece[i]==0x9 or piece[i]==0xa or piece[i]==0xd or (0x20<=piece[i] and piece[i]<=0x7e) :
                                strong+="%c" % piece[i]
                return strong, encoding, bom
        return None, None, bom

    def generateheader(self, filename, writethis):
        justfilename=self.fullfilelistdic[filename]["name"].encode("UTF-16-LE")+b'\x00\x00'
        justfilenamel=len(self.fullfilelistdic[filename]["name"])+1
        headerlength=46+len(self.fullfilelistdic[filename]["name"])*2
        record_length=headerlength+len(writethis)
        field1=(record_length).to_bytes(4, byteorder='little', signed=False)
        field2="FILE".encode("UTF-8")
        field3=(justfilenamel).to_bytes(4, byteorder='little', signed=False)
        field4=hashlib.sha256(writethis).digest()
        field5=justfilename
        bwritethis=field1+field2+field3+field4+field5+writethis
        return bwritethis

    def checkifnewfileversion(self, filename, ggpkpointer) :
        if self.isthemod is True :
            ggpkpointer.seek(self.fullfilelistdic[filename]["position"])
            beforefiledata=ggpkpointer.read(self.fullfilelistdic[filename]["length"])
            filehash=beforefiledata[12:44].hex()
            storefiletodisk=False
            if filename not in self.keeplist :
                filestart=46+len(self.fullfilelistdic[filename]["name"])*2
                self.storefiletodisk(filename, beforefiledata[filestart:])
            else :
                if self.keeplist[filename]!=filehash :
                    filestart=46+len(self.fullfilelistdic[filename]["name"])*2
                    self.storefiletodisk(filename, beforefiledata[filestart:])

    def writebinarydata(self, filename, writethis, ggpkpointer) :
        self.checkifnewfileversion(filename, ggpkpointer)
        self.onlywritebinarydata(filename, writethis, ggpkpointer)

    def onlywritebinarydata(self, filename, writethis, ggpkpointer):
        record_length=len(writethis)
        if self.isthemod is True :
            self.keeplist[filename]=writethis[12:44].hex()
        endofggpk=self.ggpksize
        if record_length<=self.fullfilelistdic[filename]["length"] :
            ggpkpointer.seek(self.fullfilelistdic[filename]["position"])
            ggpkpointer.write(writethis)
            self.fullfilelistdic[filename]["length"]=record_length
        else :
            ggpkpointer.seek(endofggpk)
            ggpkpointer.write(writethis)
            ggpkpointer.seek(self.fullfilelistdic[filename]["referenceposition"])
            bggpksize=(endofggpk).to_bytes(8, byteorder='little', signed=False)
            ggpkpointer.write(bggpksize)
            self.fullfilelistdic[filename]["position"]=endofggpk
            self.fullfilelistdic[filename]["length"]=record_length
            self.ggpksize=endofggpk+record_length
        return False

    def readbinarydata(self, filename, ggpkpointer):
        ggpkpointer.seek(self.fullfilelistdic[filename]["position"])
        beforefiledata=ggpkpointer.read(self.fullfilelistdic[filename]["length"])
        filehash=beforefiledata[12:44].hex()
        if filename in self.keeplist :
            if self.keeplist[filename]!=filehash :
                self.keeplist[filename]=filehash
                filestart=46+len(self.fullfilelistdic[filename]["name"])*2
                self.storefiletodisk(filename, beforefiledata[filestart:])
                return beforefiledata[filestart:]
            return self.readstoredbinarydata(filename)
        else :
            filestart=46+len(self.fullfilelistdic[filename]["name"])*2
            return beforefiledata[filestart:]

    def readggpkbinarydata(self, filename, ggpkpointer):
        headerlength=46+len(self.fullfilelistdic[filename]["name"])*2
        size=self.fullfilelistdic[filename]["length"]-headerlength
        if size<=0 :
            return b''
        position=self.fullfilelistdic[filename]["position"]+headerlength
        if position+size>self.ggpksize :
            return None
        ggpkpointer.seek(position)
        piece = ggpkpointer.read(size)
        return piece

    def readstoredbinarydata(self, filename):
        targetfilename=os.path.join("keep", filename[2:])
        if os.path.exists(targetfilename) is False :
            return None
        with open(targetfilename, "rb") as fin :
            return fin.read()
        return None

    def storefiletodisk(self, filename, writethis):
        targetpath=os.path.join("keep", self.fullfilelistdic[filename]["path"][2:])
        if os.path.exists(targetpath) is False :
            os.makedirs(targetpath)
        targetfilename=os.path.join(targetpath, self.fullfilelistdic[filename]["name"])
        with open(targetfilename, "wb") as fout :
            fout.write(writethis)





























