#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-02-05 14:58:58 
# Copyright 2014 NONE rights reserved.

import os
import sys

frameworkPath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class iPapa(object):
    iPath = frameworkPath
    iBinPath = os.path.join(frameworkPath, 'bin')
    iConfPath = os.path.join(frameworkPath, 'conf')
    iLibPath = os.path.join(frameworkPath, 'lib')
    iOutputPath = os.path.join(frameworkPath, 'output')
    iDataPath = os.path.join(frameworkPath, 'data')
    iFramePath = os.path.join(frameworkPath, 'framework')
    iLogPath = os.path.join(frameworkPath, 'log')
    iTmpPath = os.path.join(frameworkPath, 'tmp')
    mLogger = None
    wLogger = None
    cLogger = None

sys.path = [iPapa.iBinPath, iPapa.iConfPath, iPapa.iLibPath, iPapa.iFramePath] + sys.path

# setup root logger
import logging, logger
logger.initLogBasicPath(iPapa.iLogPath)
logger.initRootLogger('iPapa', logLevel=logging.DEBUG, logDir=iPapa.iLogPath, formatStr=None, \
            when='D', backupCount=7, stdout=True)
iPapa.mLogger = logger.getSubLogger('iPapa_manager')
iPapa.wLogger = logger.getSubLogger('iPapa_worker')
iPapa.cLogger = logger.getSubLogger('iPapa_controller')




if __name__ == '__main__':
    print "\n".join([iPapa.iPath, iPapa.iBinPath, iPapa.iConfPath, iPapa.iLibPath, iPapa.iOutputPath, iPapa.iDataPath, iPapa.iFramePath, iPapa.iLogPath, iPapa.iTmpPath])
