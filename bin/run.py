#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-02-05 16:03:29 
# Copyright 2014 NONE rights reserved.

import setup
from setup import iPapa
import logger
import logging
from iManager import WorkManager


if __name__ == '__main__':
    m = WorkManager(2) 
    m.start() 

