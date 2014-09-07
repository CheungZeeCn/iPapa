#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-30 13:39:17 
# Copyright 2014 NONE rights reserved.


"""
by this prog, I gen the keylist.
"""

from setup import iPapa
import sys
import os
import util
import time
import re
import shutil


theTime = time.time( ) #- 3600*24

outputPath = iPapa.iOutputPath
dataPath = iPapa.iDataPath
#izhuomiDir = "/Users/cheungzee/opdir/bstrp/izhuomi-data"
#monStr = time.strftime('%Y%m', time.localtime(theTime))
#monUrl = 'izhuomi-data/' + monStr + '/'
#copyToPath = os.path.join(izhuomiDir, monStr)

def updateToday():
    dayStr = time.strftime('%Y%m%d', time.localtime(theTime))
    dirList = os.listdir(outputPath)
    for tsDir in dirList:
        if tsDir.startswith(dayStr):
            doneList = gen(tsDir)
            writeDoneList(doneList, tsDir)


def writeDoneList(doneList, tsDir):
    fName = os.path.join(dataPath, 'klist.%s.txt' % (tsDir))
    isOK = False
    with open(fName, 'w') as f:
        for k in doneList:
            f.write("%s\n" % k)
        isOK = True
        print "write file %s" % fName
    return isOK

def gen(tsDir):
    #find today's keyfiles 
    doneList = []
    for f in os.walk(os.path.join(outputPath, tsDir)):
        if os.path.basename(f[0]).startswith('_content_') and f[1] == []:
            key = os.path.basename(f[0])
            status, error = checkKeyDir(f)         
            if status == "ERROR":
                print "ERROR:", key, error   
            elif status == "IGNORE":
                pass
            else:
                doneList.append(key)
    return doneList

def checkKeyDir(f):
    error = []
    status = 'OK'
    meta = None
    key = os.path.basename(f[0])

    if 'meta.json' not in  f[2]:
        error.append("no meta file !")
        status = 'ERROR'
    else:
        meta = util.loadJsonFile(os.path.join(f[0], 'meta.json'))
        if 'isIgnore' in meta and meta['isIgnore'] == True:
            status = 'IGNORE'
            error = []
            return status, error
            
    if 'content.html' not in  f[2]:
        error.append("no content file !")
        status = 'ERROR'
    if 'content.mp3' not in f[2]:
        error.append("no mp3 file !")
        status = 'ERROR'
    if '__zipPic__.jpg' not in f[2] and '__zipPic__.png' not in f[2]:
        error.append("no zipPic file !")
        status = 'ERROR'

    meta = util.loadJsonFile(os.path.join(f[0], 'meta.json'))
    if meta:
        #check embPic:
        for picName in meta['embPics']:
            if util.getUrlFileName(picName) not in f[2]:
                error.append("no embPic %s !" % (util.getUrlFileName(picName)))
                status = 'ERROR'
    return status, error


if __name__ == '__main__':
    updateToday()
    #check output dir
    #for each key dir
    #check it


    #report, okKeys = check(sys.argv[1])
    #for k in report:
    #    print k, report[k]
    #with open('doneKey.list', 'w') as f:
    #    for k in okKeys:
    #        f.write("%s\n"%k) 

