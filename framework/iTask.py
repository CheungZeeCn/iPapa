#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-24 13:55:53 
# Copyright 2014 NONE rights reserved.

import time
import util

class Task(dict):
    """
    taskId: assign by manager
    status: 
        new: new status, just init, should be put into the inQueueDown
        down:  downloading
        downed:  downloade
        parsing: parsing
        //store, stored
        done: done
        failed: failed
    taskType: 
        'page' for download and parse
        'media' for download into tmpDir and then mv by the Parser
    """
    def __init__(self, taskId, status='new', url='', handler='common', handleBy='', 
                        repeatTime=0, tryTimes=3, waitTime=30, taskType='page', msg='new', 
                        postdata={}, data={}, ref='', dest=''):
        dict.__init__(self)       
        self.id = taskId
        self.status = status
        self.url = url
        self.ref = ref
        self.handler = handler
        self.handleBy = handleBy
        self.taskType = taskType
        self.update(data) 
        self.repeatTime = repeatTime
        self.tryTimes = tryTimes
        self.timeout = waitTime
        self.msg = msg
        self.ts = time.time()
        self.signTs = []
        self.postdata = postdata
        self.dest = dest

    def exprMe(self):
        retDict = {}
        for k in ('id', 'status', 'url', 'ref', 'handler', 'handleBy', 
                'taskType', 'repeatTime', 'tryTimes', 'timeout', 'msg', 
                'ts', 'signTs', 'postdata', 'dest'):
            retDict[k] = getattr(self, k)
        return util.dump2JsonStr(retDict).encode('utf-8')

    
if __name__ == '__main__':
    a = Task(1, data={1:2, 3:4})
    print a

