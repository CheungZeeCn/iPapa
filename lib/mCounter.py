#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-24 15:45:02 
# Copyright 2014 NONE rights reserved.

import threading

class mCounter(object):
    def __init__(self, v=0):
        self.v = v
        self.l = threading.Lock()

    def get(self):
        v = None
        self.l.acquire()
        v = self.v
        self.l.release()
        return v

    def set(self, v):
        self.l.acquire()
        self.v = v
        self.l.release()
        return True

    def inc(self, n=1):
        v = None
        self.l.acquire()
        self.v += n
        v = self.v
        self.l.release()
        return v

    def sub(self, n=1):
        self.l.acquire()
        self.v -= n
        v = self.v
        self.l.release()
        return v


if __name__ == '__main__':
    a = mCounter()



