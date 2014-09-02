#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-02-05 16:03:29 
# Copyright 2014 NONE rights reserved.

import setup
# import config class
from setup import iPapa
#import logger
#import logging
from iManager import WorkManager
from iTask import Task
import conf


# start the program

if __name__ == '__main__':
    # 1. setup first task or tasks
    seedTask = Task(1, url='http://learningenglish.voanews.com/content/mount-vernon-george-washington/1849481.html', handler='ContentPageHandler')
    seedTask['key'] = '_content_mount-vernon-george-washington_1849481.html'

    #initTask, threadNum 3 for download, parserNum 2 for parse it
    #m = WorkManager(seedTask, conf.iWorkThreadNum, conf.iParserThreadNum, False)
    m = WorkManager(seedTask, conf.iWorkThreadNum, conf.iParserThreadNum, False)

    m.start() 

