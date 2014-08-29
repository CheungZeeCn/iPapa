#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-24 21:07:29 
# Copyright 2014 NONE rights reserved.

from bs4 import BeautifulSoup as BS
from iTask import Task
import os
from setup import iPapa

class PicHandler(object):
    def parse(self, task):
        if task['picType'] == 'zipPic':
            fileLoc = os.path.join(iPapa.iTsOutputPath, task.dest)
            newLoc = os.path.join(os.path.dirname(fileLoc), '__zipPic__'+os.path.splitext(fileLoc)[1])
            print fileLoc, newLoc
            os.rename(fileLoc, newLoc)
        elif task['picType'] == 'contentPic': 
            fileLoc = os.path.join(iPapa.iTsOutputPath, task.dest)
            newLoc = os.path.join(os.path.dirname(fileLoc), 'content'+os.path.splitext(fileLoc)[1])
            print fileLoc, newLoc
            print task
            os.rename(fileLoc, newLoc)
        elif task['picType'] == 'embPic': 
            pass 
        else:
            pass
        return {}

if __name__ == '__main__':
    data = open('tmp').read()
    m = ClassPageHandler()
    m.parserContent(data)

