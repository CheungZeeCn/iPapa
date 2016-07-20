#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2016-07-20 12:45:34 
# Copyright 2016 NONE rights reserved.

import sys
import os
import util
import datetime


def genKlist(theDir):
    report = {}
    okKeys = []
    tsDir = os.path.dirname(theDir)

    for f in os.walk(theDir):
        if f[1] != []:  
            continue

        error = []
        meta = None
        key = os.path.basename(f[0])

        if 'meta.json' not in  f[2]:
            error.append("no meta file !")
        else:
            meta = util.loadJsonFile(os.path.join(f[0], 'meta.json'))
            if 'isIgnore' in meta and meta['isIgnore'] == True:
                report[key] = ["ignored:%s" % meta['ignoreMsg'], ]
                okKeys.append(key)
                continue

        if 'content.html' not in  f[2]:
            error.append("no content file !")
        if 'content.mp3' not in f[2]:
            error.append("no mp3 file !")
        if '__zipPic__.jpg' not in f[2] and '__zipPic__.png' not in f[2]:
            error.append("no zipPic file !")
            
        #if meta:
        #    #check embPic:
        #    for picName in meta['embPics']:
        #        if util.getUrlFileName(picName) not in f[2]:
        #            error.append("no embPic %s !" % (util.getUrlFileName(picName)))
        if error != []:
            report[key] = error
        else:
            okKeys.append(key)
    return (report, okKeys)

def storeKlist(okKeys, dstPath):
    with open(dstPath, 'w') as f:
        for i in okKeys:   
            f.write(i+"\n")

if __name__ == '__main__':
    outputPath = sys.argv[1].rstrip('/')
    kListPath = sys.argv[2]

    report, okKeys = genKlist(outputPath)

    
    print >> sys.stderr, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print >> sys.stderr, "BEGIN, dir: %s" % (outputPath)
    storeKlist(okKeys, os.path.join(kListPath, "klist." + os.path.basename(outputPath)))
    for k in report:
        print >> sys.stderr, "ERROR: key[%s] errorlist[ %s ]" %(k, report[k])
    print >> sys.stderr, "END, dir: %s" % (outputPath)


