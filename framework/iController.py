#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-24 19:57:16 
# Copyright 2014 NONE rights reserved.

import threading
import logging
import time
import Queue
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler 
import HttpWatcher

myLogger = None
if 'iPapa_controller' not in logging.Logger.manager.loggerDict:
    myLogger = logging.getLogger()
else:
    myLogger = logging.getLogger('iPapa_controller')

class Controller(threading.Thread):
    def __init__(self, myManager):
        threading.Thread.__init__(self, name='controller')
        self.m = myManager
        self.timeStampBegin = time.time()
        self.daemon = True
    
    def isAllDone(self):
        return self.myManager.isAllDone()

    def run(self):
        HttpWatcher.run(port=28282, m=self.m)

if __name__ == '__main__':
    print 'hello world'


