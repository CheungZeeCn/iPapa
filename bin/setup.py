#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-02-05 14:58:58 
# Copyright 2014 NONE rights reserved.
# A Class that setup all the settings here for the framework.
# Include the paths mainly only, and do some logger setup

import os
import sys

frameworkPath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class iPapa(object):
    # path of all the program inclueding the framwork. may be "../" 
    iPath = frameworkPath  
    # binPath storing the logic program for the crawler and sth like that
    iBinPath = os.path.join(frameworkPath, 'bin')
    # configuration
    iConfPath = os.path.join(frameworkPath, 'conf')
    # lib
    iLibPath = os.path.join(frameworkPath, 'lib')
    # output data here
    iOutputPath = os.path.join(frameworkPath, 'output')
    # will be update by manager later
    iTsOutputPath = os.path.join(iOutputPath, '00000000')
    # input data here
    iDataPath = os.path.join(frameworkPath, 'data')
    # framework program here
    iFramePath = os.path.join(frameworkPath, 'framework')
    # logPath
    iLogPath = os.path.join(frameworkPath, 'log')
    # tmp
    iTmpPath = os.path.join(frameworkPath, 'tmp')
    #manerger Logger
    mLogger = None
    #workers' Logger
    wLogger = None
    #controller Logger
    cLogger = None

sys.path = [iPapa.iBinPath, iPapa.iConfPath, iPapa.iLibPath, iPapa.iFramePath] + sys.path

# setup root logger
import logging, logger
logger.initLogBasicPath(iPapa.iLogPath)
#iPapa.log as log file, and we cut it everyday while storing it for 7 days.
logger.initRootLogger('iPapa', logLevel=logging.DEBUG, logDir=iPapa.iLogPath, formatStr=None, \
            when='D', backupCount=7, stdout=True)

iPapa.mLogger = logger.getSubLogger('iPapa_manager')
iPapa.wLogger = logger.getSubLogger('iPapa_worker')
iPapa.pLogger = logger.getSubLogger('iPapa_parser')
iPapa.cLogger = logger.getSubLogger('iPapa_controller')


if __name__ == '__main__':
    # print out the paths
    print "\n".join([iPapa.iPath, iPapa.iBinPath, iPapa.iConfPath, iPapa.iLibPath, iPapa.iOutputPath, iPapa.iDataPath, iPapa.iFramePath, iPapa.iLogPath, iPapa.iTmpPath])
# It's a sentence.

