#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-24 21:07:29 
# Copyright 2014 NONE rights reserved.

from bs4 import BeautifulSoup as BS
from iTask import Task
import os
from setup import iPapa

class AudioHandler(object):
    def parse(self, task):
        if task['audioType'] == 'MP3':
            fileLoc = os.path.join(iPapa.iTsOutputPath, task.dest)
            newLoc = os.path.join(os.path.dirname(fileLoc), 'content.mp3')
            print fileLoc, newLoc
            os.rename(fileLoc, newLoc)
        else:
            fileLoc = os.path.join(iPapa.iTsOutputPath, task.dest)
            newLoc = os.path.join(os.path.dirname(fileLoc), 'content.mp3')
            print fileLoc, newLoc
            os.rename(fileLoc, newLoc)
        return {}

if __name__ == '__main__':
    data = open('tmp').read()
    m = ClassPageHandler()
    m.parserContent(data)

