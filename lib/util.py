#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2013-11-18 19:25:15 
# Copyright 2013 NONE rights reserved.

import re
import time
import pickle
from string import punctuation
import logging

def initLog():
    formatStr = ('%(asctime)s [%(levelname)s][%(filename)s:%(lineno)s]:'
                ' %(message)s')
    logging.basicConfig(format=formatStr, level=logging.DEBUG)


def psList(a):
    retString = '['
    ret = []
    for each in a:
        if type(each) == list:
            ret.append(psList(each))
        else:   
            ret.append(each)
    retString += ", ".join(ret)
    retString += ']'
    return retString

def emptySplit(text):
    re_empty = re.compile('\s+')
    return re_empty.split(text)

def readSplFile(fn):
    ret = []
    with open(fn, 'r') as f:
        for l in f:
            wList = emptySplit(l.strip())
            ret.append(wList)
    return ret

def getTimeStr(theTime=None):
    if theTime == None:
        theTime = time.time()
    timeStr = time.strftime('%Y-%m-%d %H:%M:%S', \
                time.localtime(theTime))
    return timeStr

def getTimeStamp(theTime=None):
    if theTime == None:
        theTime = time.time()
    timeStr = time.strftime('%Y%m%d%H%M%S', \
                time.localtime(theTime))
    return timeStr

def dump2Pickle(data, fname):
    print "dump into [%s]" % (fname)
    #print data
    with open(fname, 'w') as f:
        pickle.dump(data, f)
    print "done"

def loadPickle(fname):
    print "load from [%s]" % (fname)
    ret = None
    try:
        with open(fname, 'r') as f:
            ret = pickle.load(f)
    except Exception, e:
        return None  
    print "done"
    return ret

def load_stopwords(stops, file):
    for line in file:
        stops.add(line.strip())

def f11(preList, realList):
    '''f1 score'''
    p = set(preList)
    r = set(realList)
    tp = float(len(p & r))
    fp = float(len(p - r))
    fn = float(len(r -p))
    pp = tp/(tp+fp)
    rr = tp/(tp+fn)
    if tp == 0:
        return (0, 0, 0)
    else:
        return ((2 * pp * rr) / (pp + rr), pp, rr)

def f1(preList, realList):
    '''f1 score'''
    p = set(preList)
    r = set(realList)
    tp = float(len(p & r))
    fp = float(len(p - r))
    fn = float(len(r -p))
    pp = tp/(tp+fp)
    rr = tp/(tp+fn)
    if tp == 0:
        return 0
    else:
        return (2 * pp * rr) / (pp + rr)

def getTopN(d, n):
    return sorted(d.items(), key=lambda d:d[1], reverse=True)[:n]   

if __name__ == '__main__':
    print 'hello world'

