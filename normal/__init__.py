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
import threading
import queue
from tkinter import *
import poemods_threads

modifyggpk = "C:\\games\\poe\\Content.ggpk"
defragggpk = "C:\\games\\poe\\Content2.ggpk"
windowgeometry="866x714+0+0"
configfile="poemods_config.txt"
excludefile="exclude.txt"

actionqueue=queue.Queue()
searchqueue=queue.Queue()
viewqueue=queue.Queue()
modsthreads=poemods_threads.manager(actionqueue, searchqueue, viewqueue)

def updatemessage():
    lastmessage=None
    while modsthreads.sendmessage.qsize()>0 :
        newmessage=modsthreads.sendmessage.get()
        if len(newmessage)==4 :
            if newmessage[1]=="modify" :
                if newmessage[2] in autocheck :
                    if newmessage[3] is True :
                        autocheck[newmessage[2]][1].configure(bg="#ff9090")
                    else :
                        autocheck[newmessage[2]][1].configure(bg=defaultbgcolor)
            if newmessage[1] in tkthingy  :
                if newmessage[3] is True :
                    tkthingy[newmessage[1]].configure(bg="#ff9090")
                else :
                    tkthingy[newmessage[1]].configure(bg=defaultbgcolor)
        elif len(newmessage)==2 :
            if newmessage[1]=="error" :
                status.set(newmessage[0])
                time.sleep(5)
        lastmessage=newmessage[0]
    if lastmessage is not None :
        status.set(lastmessage)
    root.after(250, updatemessage)

def updatelist():
    while modsthreads.sendsearch.qsize()>1 :
        modsthreads.sendsearch.get()
    if modsthreads.sendsearch.qsize()>=1 :
        matchinglist=modsthreads.sendsearch.get()
        filelistmatch.delete(0, END)
        for ismatching in matchinglist :
            filelistmatch.insert(END, ismatching)
        labellistsize.set("%d files" % (len(matchinglist)))
    root.after(250, updatelist)

def leftclickonthelist(event) :
    global filelistmatchcurselection
    filelistmatchcurselection=""

def updateview():
    global filelistmatchcurselection
    newselection=filelistmatch.curselection()
    if len(newselection)>0 :
        newselectionname=filelistmatch.get(newselection)
        if newselectionname!=filelistmatchcurselection :
            filelistmatchcurselection=newselectionname
            viewqueue.put(["view", filelistmatchcurselection])
    while modsthreads.sendview.qsize()>1 :
        modsthreads.sendview.get()
    if modsthreads.sendview.qsize()>=1 :
        displaythis=modsthreads.sendview.get()
        labelreadnamel.delete('1.0', END)
        labelreadnamel.insert(INSERT, displaythis[0])

        leftsize=len(displaythis[1])
        leftsizeh="%d" % (leftsize)
        if leftsize/1000000.0>=1.0 :
            leftsizeh="%.6f Mo" % (leftsize/1000000.0)
        elif leftsize/1000.0>=1.0 :
            leftsizeh="%.3f Ko" % (leftsize/1000.0)
        else :
            leftsizeh="%d o" % (leftsize)
        labelreadb.set("Original file : %s" % (leftsizeh))
        textreadb.delete('1.0', END)
        textreadb.insert(INSERT, str(displaythis[1]))

        if displaythis[3] is False :
            rightsize=len(displaythis[2])
            rightsizeh="%d" % (rightsize)
            if rightsize/1000000.0>=1.0 :
                rightsizeh="%.6f Mo" % (rightsize/1000000.0)
            elif rightsize/1000.0>=1.0 :
                rightsizeh="%.3f Ko" % (rightsize/1000.0)
            else :
                rightsizeh="%d o" % (rightsize)
        else :
            rightsizeh=leftsizeh
        labelreadm.set("Yours : %s" % (rightsizeh))
        textreadm.delete('1.0', END)
        textreadm.insert(INSERT, str(displaythis[2]))

        if displaythis[3] is False :
            labelreadml.configure(bg="#ff9090")
            framereadm.pack(side=LEFT, fill=BOTH, expand=1)
        else :
            framereadm.pack_forget()
    root.after(100, updateview)

def framegmcallback():
    global modifyggpk
    modifyggpk=entrygm.get()
    actionqueue.put(["scan modg", modifyggpk, True])

def framegdcallback():
    global defragggpk
    defragggpk=entrygd.get()
    actionqueue.put(["defragment", defragggpk])

def getrestrict():
    wesearchonly=[]
    wesearchonlythese=textsearchonly.get('1.0', END).split("\n")
    for onlysearch in wesearchonlythese :
        if len(onlysearch)>0 :
            wesearchonly.append(onlysearch)
    return wesearchonly

def getexclude():
    wesearchnot=[]
    wesearchnotthese=textsearchnot.get('1.0', END).split("\n")
    for notsearch in wesearchnotthese :
        if len(notsearch)>0 :
            wesearchnot.append(notsearch)
    return wesearchnot

def framesearchcallback():
    global filelistmatchcurselection
    filelistmatchcurselection=""
    restrict=getrestrict()
    exclude=getexclude()
    searchqueue.put(["search", [], [], restrict, exclude])

def differentcallback():
    global filelistmatchcurselection
    filelistmatchcurselection=""
    restrict=getrestrict()
    exclude=getexclude()
    actionqueue.put(["different", [], [], restrict, exclude])

def samecallback():
    global filelistmatchcurselection
    filelistmatchcurselection=""
    restrict=getrestrict()
    exclude=getexclude()
    actionqueue.put(["same", [], [], restrict, exclude])

def extractcallback():
    restrict=getrestrict()
    exclude=getexclude()
    actionqueue.put(["extract", [], [], restrict, exclude])

def insertcallback():
    restrict=getrestrict()
    exclude=getexclude()
    actionqueue.put(["insert", [], [], restrict, exclude])

def savedefaultpath():
    global windowgeometry
    windowgeometry=root.geometry()
    with open(configfile, "w") as confout :
        confout.write("PoEFile="+modifyggpk+"\n")
        confout.write("DefragmentedFile="+defragggpk+"\n")
        confout.write("Geometry="+windowgeometry+"\n")

def getdefaultpath():
    global modifyggpk, defragggpk, windowgeometry
    if os.path.exists(configfile) :
        with open(configfile, "r", encoding="utf-8") as fin :
            for line in fin :
                if re.search(r'PoEFile=', line) is not None :
                    modifyggpk = re.sub(r'.*=(.*?)[\n$]', r'\1', line)
                    entrygm.delete(0, END)
                    entrygm.insert(0, modifyggpk)
                elif re.search(r'DefragmentedFile=', line) is not None :
                    defragggpk = re.sub(r'.*=(.*?)[\n$]', r'\1', line)
                    entrygd.delete(0, END)
                    entrygd.insert(0, defragggpk)
                elif re.search(r'Geometry=', line) is not None :
                    windowgeometry = re.sub(r'.*=(.*?)[\n$]', r'\1', line)
                    root.geometry(windowgeometry)
    else :
        savedefaultpath()

def restoreopcallback():
    restrict=[]
    exclude=[]
    restrict=getrestrict()
    exclude=getexclude()
    if len(restrict)>0 or len(exclude)>0 :
        actionqueue.put(["restore", [], [], restrict.copy(), exclude.copy()])

def restorecallback():
    automodsexecute(True)

def applycallback():
    automodsexecute(False)

def automodsexecute(restore):
    global automodspickedup
    automodspickedup=automodsel.get()
    restrict=[]
    exclude=[]
    exclude=getexclude()
    nothingrestored=True
    ignorelist=[]
    for title in autocheck :
        if autocheck[title][0].get()==0 :
            ignorelist.append(title)
    filename=automodslist[automodspickedup]
    fileloc=os.path.join("automods", filename)
    if os.path.exists(fileloc) :
        with open(fileloc, "r", encoding="UTF-8") as fio :
            restrictfilter=[]
            excludefilter=[]
            lasttitle="nimporte"
            bloque=False
            for line in fio :
                replace=re.search(r'^(\w+)\s+\"(.*?)\"', line)
                if replace is not None :
                    if replace.group(1)=="title" :
                        if replace.group(2) in ignorelist :
                            lasttitle="nimporte"
                            bloque=True
                        else :
                            lasttitle=replace.group(2)
                            bloque=False
                        restrictfilter.clear()
                        excludefilter.clear()
                    if bloque is False :
                        if replace.group(1)=="restriction" :
                            restrictfilter.append(replace.group(2))
                        elif replace.group(1)=="exclude" :
                            excludefilter.append(replace.group(2))
                        elif replace.group(1)=="execute" :
                            if restore is True :
                                actionqueue.put(["restore", restrictfilter.copy(), excludefilter.copy(), restrict.copy(), exclude.copy()])
                                nothingrestored=False
                            else :
                                actionqueue.put(["modify", restrictfilter.copy(), excludefilter.copy(), restrict.copy(), exclude.copy(), replace.group(2), lasttitle])
                            restrictfilter.clear()
                            excludefilter.clear()
                        elif replace.group(1)=="restore" :
                            actionqueue.put(["restore", restrictfilter.copy(), excludefilter.copy(), restrict.copy(), exclude.copy()])
                            nothingrestored=False
                            restrictfilter.clear()
                            excludefilter.clear()
                        elif replace.group(1)=="extract" :
                            actionqueue.put(["extract", restrictfilter.copy(), excludefilter.copy(), restrict.copy(), exclude.copy()])
                            restrictfilter.clear()
                            excludefilter.clear()
                        elif replace.group(1)=="insert" :
                            if restore is True :
                                actionqueue.put(["restore", restrictfilter.copy(), excludefilter.copy(), restrict.copy(), exclude.copy()])
                                nothingrestored=False
                            else :
                                actionqueue.put(["insert", restrictfilter.copy(), excludefilter.copy(), restrict.copy(), exclude.copy()])
                            restrictfilter.clear()
                            excludefilter.clear()
                        elif replace.group(1)=="replacewith" :
                            if restore is True :
                                actionqueue.put(["restore", restrictfilter.copy(), excludefilter.copy(), restrict.copy(), exclude.copy()])
                                nothingrestored=False
                            else :
                                actionqueue.put(["replacewith", restrictfilter.copy(), excludefilter.copy(), restrict.copy(), exclude.copy(), replace.group(2)])
                            restrictfilter.clear()
                            excludefilter.clear()
                        elif replace.group(1)=="replacewithasset" :
                            if restore is True :
                                actionqueue.put(["restore", restrictfilter.copy(), excludefilter.copy(), restrict.copy(), exclude.copy()])
                                nothingrestored=False
                            else :
                                actionqueue.put(["replacewithasset", restrictfilter.copy(), excludefilter.copy(), restrict.copy(), exclude.copy(), replace.group(2)])
                            restrictfilter.clear()
                            excludefilter.clear()
    #if restore is True and nothingrestored is True :
    #    if len(restrict)>0 or len(exclude)>0 :
    #        actionqueue.put(["restore", [], [], restrict.copy(), exclude.copy()])

def selectsearchcallback():
    global automodspickedup
    automodspickedup=automodsel.get()
    textsearchonly.delete('1.0', END)
    textsearchnot.delete('1.0', END)
    ignorelist=[]
    for title in autocheck :
        if autocheck[title][0].get()==0 :
            ignorelist.append(title)
    filename=automodslist[automodspickedup]
    fileloc=os.path.join("automods", filename)
    if os.path.exists(fileloc) :
        with open(fileloc, "r", encoding="UTF-8") as fio :
            bloque=False
            for line in fio :
                replace=re.search(r'^(\w+)\s+\"(.*?)\"', line)
                if replace is not None :
                    if replace.group(1)=="title" :
                        if replace.group(2) in ignorelist :
                            bloque=True
                        else :
                            bloque=False
                    if bloque is False :
                        if replace.group(1)=="restriction" :
                            textsearchonly.insert(END, replace.group(2)+"\n")
                        elif replace.group(1)=="exclude" :
                            textsearchnot.insert(END, replace.group(2)+"\n")

def onchangeautomodsfile(*args):
    global automodspickedup
    automodspickedup=automodsel.get()
    filename=automodslist[automodspickedup]
    for title in autocheck :
        autocheck[title][1].destroy()
    frameautocheck.pack_forget()
    frameexecute.pack_forget()
    autocheck.clear()
    fileloc=os.path.join("automods", filename)
    if os.path.exists(fileloc) :
        with open(fileloc, "r", encoding="UTF-8") as fio :
            for line in fio :
                replace=re.search(r'^title\s+\"(.*?)\"', line)
                if replace is not None :
                    title=replace.group(1)
                    autocheck[title]=[IntVar(), None]
                    autocheck[title][1]=Checkbutton(frameautocheck, text=title, font=(myfontfamily, myfontsize), variable=autocheck[title][0], fg="#000000", onvalue=1, offvalue=0, height=1)
                    autocheck[title][1].pack(anchor=W)
    frameautocheck.pack(anchor=W)
    frameexecute.pack(side=BOTTOM, fill=BOTH, pady=10)

def framegdexpcallback():
    framegd.pack(fill=X)

root = Tk()

defaultbgcolor="#ffffff"
winfo_geometry = root.geometry()
root.geometry(windowgeometry)
defaultbgcolor=root.cget("background")
tkthingy={}

myfontfamily="Helvetica"
myfontsize=8

frametop=Frame(root)

status=StringVar()
statuslbl=Label(frametop, textvariable=status, bg="black", fg="yellow")
statuslbl.pack(fill=X)

frametopleft=Frame(frametop)

framegm=Frame(frametopleft)
Label(framegm, text="Path to your Path of Exile Content.ggpk : ", font=(myfontfamily, myfontsize)).pack(side=LEFT)
entrygm = Entry(framegm, font=(myfontfamily, myfontsize), width=80)
entrygm.pack(side=LEFT)
tkthingy["scan modg"]=Button(framegm, text ="Scan", font=(myfontfamily, myfontsize), command = framegmcallback)
tkthingy["scan modg"].pack(side=LEFT, padx=15)
Button(framegm, text ="Defragment", font=(myfontfamily, myfontsize), command = framegdexpcallback).pack(side=LEFT)
framegm.pack(fill=X)

framegd=Frame(frametopleft)
Label(framegd, text="Path to your defragmented Content.ggpk : ", font=(myfontfamily, myfontsize)).pack(side=LEFT)
entrygd = Entry(framegd, font=(myfontfamily, myfontsize), width=80)
entrygd.pack(side=LEFT)
tkthingy["defragment"]=Button(framegd, text ="Defragment now", font=(myfontfamily, myfontsize), command = framegdcallback)
tkthingy["defragment"].pack(side=LEFT, padx=15)
framegd.pack_forget()

frametopleft.pack(fill=X)

frametop.pack(fill=X)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

framebottom=Frame(root)

frameleft=Frame(framebottom)

framesearchfound=Frame(frameleft)

framesearch=Frame(framesearchfound)

frameexecute4=Frame(framesearch)
framesearchonly=Frame(frameexecute4)

scrollbarsearchonly = Scrollbar(framesearchonly)
scrollbarsearchonly.pack(side=RIGHT, fill=Y)
textsearchonly=Text(framesearchonly, bg="#c0e0c0", width=35, height=3, font=(myfontfamily, myfontsize), yscrollcommand = scrollbarsearchonly.set)
textsearchonly.pack(fill=X, expand=1)
scrollbarsearchonly.config(command=textsearchonly.yview)

framesearchonly.pack(side=LEFT, fill=X, expand=1)

framesearchnot=Frame(frameexecute4)

scrollbarsearchnot = Scrollbar(framesearchnot)
scrollbarsearchnot.pack(side=RIGHT, fill=Y)
textsearchnot=Text(framesearchnot, bg="#e0c0c0", width=35, height=3, font=(myfontfamily, myfontsize), yscrollcommand = scrollbarsearchnot.set)
if os.path.exists(excludefile) :
    with open(excludefile, "r", encoding="utf-8") as fin :
        for line in fin :
            textsearchnot.insert(END, line)
textsearchnot.pack(fill=X, expand=1)
scrollbarsearchnot.config(command=textsearchnot.yview)

framesearchnot.pack(side=LEFT, fill=X, expand=1)
frameexecute4.pack(fill=X, expand=1)

frameexecute2=Frame(framesearch)
Label(frameexecute2, font=(myfontfamily, myfontsize), text="restrict filter").pack(side=LEFT, expand=1, fill=X, anchor=E)
tkthingy["restoreop"]=Button(frameexecute2, text ="Restore", font=(myfontfamily, myfontsize), command = restoreopcallback)
tkthingy["restoreop"].pack(side=LEFT)
tkthingy["extract"]=Button(frameexecute2, text ="Extract", font=(myfontfamily, myfontsize), command = extractcallback)
tkthingy["extract"].pack(side=LEFT)
tkthingy["insert"]=Button(frameexecute2, text ="Insert", font=(myfontfamily, myfontsize), command = insertcallback)
tkthingy["insert"].pack(side=LEFT)
Button(frameexecute2, text ="Search", font=(myfontfamily, myfontsize), command = framesearchcallback).pack(side=LEFT)
Label(frameexecute2, font=(myfontfamily, myfontsize), text="exclude filter").pack(side=LEFT, expand=1, fill=X, anchor=W)
frameexecute2.pack(fill=X, expand=1)

framesearch.pack(fill=X)

framelist=Frame(framesearchfound)
scrollbarlist = Scrollbar(framelist)
scrollbarlist.pack(side=RIGHT, fill=Y)
filelistmatch = Listbox(framelist, height=20, font=(myfontfamily, myfontsize), yscrollcommand = scrollbarlist.set)
filelistmatch.bind("<Button-1>", leftclickonthelist)
filelistmatch.pack(fill=X)
scrollbarlist.config(command=filelistmatch.yview)
filelistmatchcurselection=""
framelist.pack(fill=X)

framesearchfound.pack(fill=X)

frameview=Frame(frameleft)

framelistinfo=Frame(frameview)
labellistsize=StringVar()
Label(framelistinfo, font=(myfontfamily, myfontsize), textvariable=labellistsize, justify=LEFT).pack(side=LEFT)
labelreadnamel=Text(framelistinfo, font=(myfontfamily, myfontsize), height=1)
labelreadnamel.pack(side=LEFT, fill=X, expand=1)
framelistinfo.pack(fill=X)

framereadb=Frame(frameview)

labelreadb=StringVar()
labelreadbl=Label(framereadb, font=(myfontfamily, myfontsize), textvariable=labelreadb)
labelreadbl.pack(fill=X)

scrollbarreadb = Scrollbar(framereadb)
scrollbarreadb.pack(side=RIGHT, fill=Y)
textreadb=Text(framereadb, bg="#f5f5f5", width=35, font=(myfontfamily, myfontsize), yscrollcommand = scrollbarreadb.set)
textreadb.pack(fill=BOTH, expand=1)
scrollbarreadb.config(command=textreadb.yview)

framereadb.pack(side=LEFT, fill=BOTH, expand=1)

framereadm=Frame(frameview)

labelreadm=StringVar()
labelreadml=Label(framereadm, font=(myfontfamily, myfontsize), textvariable=labelreadm)
labelreadml.pack(fill=X)

scrollbarreadm = Scrollbar(framereadm)
scrollbarreadm.pack(side=RIGHT, fill=Y)
textreadm=Text(framereadm, width=35, font=(myfontfamily, myfontsize), yscrollcommand = scrollbarreadm.set)
textreadm.pack(fill=BOTH, expand=1)
scrollbarreadm.config(command=textreadm.yview)

framereadm.pack(side=LEFT, fill=BOTH, expand=1)

frameview.pack(side=LEFT, fill=BOTH, expand=1)

frameleft.pack(side=LEFT, fill=BOTH, expand=1)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

frametrsel=Frame(framebottom)
automodsel = StringVar()
first=""
automodslist={}
automodsfolder="automods"
for automodsfile in os.listdir(automodsfolder) :
    if automodsfile.endswith(".txt") :
        fileloc=os.path.join(automodsfolder, automodsfile)
        with open(fileloc, "r", encoding="UTF-8") as fio :
            for line in fio :
                replace=re.search(r'^name\s+\"(.*?)\"', line)
                if replace is not None :
                    automodslist[replace.group(1)]=automodsfile
automodspickedup=""
automodslist[automodspickedup]="None"
automodsel.set(automodspickedup)
Label(frametrsel, font=(myfontfamily, myfontsize), text="Automods : ").pack(side=LEFT)
popupMenu = OptionMenu(frametrsel, automodsel, *automodslist)
popupMenu.pack(side=LEFT)
popupMenu.configure(font=(myfontfamily, myfontsize))
automodsel.trace('w', onchangeautomodsfile)
frametrsel.pack(side=TOP, padx=15, pady=15)

frameright=Frame(framebottom)

framechoice=Frame(frameright)

frameautocheck=Frame(framechoice)
autocheck={}
frameautocheck.pack(anchor=W)

frameexecute=Frame(framechoice)

Button(frameexecute, text="View mod's master filters", font=(myfontfamily, myfontsize), command = selectsearchcallback).pack()
framechoice.pack(anchor=W, pady=10)

frameexecutegd=Frame(frameexecute)
filterselect = IntVar()
Checkbutton(frameexecutegd, text = "Use your restrict / exclude filter as well", font=(myfontfamily, myfontsize), variable = filterselect, onvalue = 1, offvalue = 1).pack(anchor=CENTER)
frameexecutein=Frame(frameexecutegd)
tkthingy["modify"]=Button(frameexecutein, text ="Modify", font=(myfontfamily, myfontsize), command = applycallback)
tkthingy["modify"].pack(side=LEFT)
tkthingy["restore"]=Button(frameexecutein, text ="Restore", font=(myfontfamily, myfontsize), command = restorecallback)
tkthingy["restore"].pack(side=LEFT)
frameexecutein.pack()
frameexecutegd.pack(fill=X, pady=20)

frameexecute.pack(fill=X, pady=10)

frameright.pack(fill=Y)

framebottom.pack(fill=BOTH, expand=1)

def quitcallback():
    savedefaultpath()
    actionqueue.put(["quit"])
    searchqueue.put(["quit"])
    viewqueue.put(["quit"])
    root.destroy()

getdefaultpath()
# force rescan in case of errors
# actionqueue.put(["scan modg", modifyggpk ,True])
actionqueue.put(["scan modg", modifyggpk ,False])

root.protocol("WM_DELETE_WINDOW", quitcallback)
updatelist()
updatemessage()
updateview()
root.mainloop()









