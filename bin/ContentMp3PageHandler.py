#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-24 21:07:29 
# Copyright 2014 NONE rights reserved.


from setup import iPapa
from bs4 import BeautifulSoup as BS
import os
import urlparse
from iTask import Task
import util

class ContentMp3PageHandler(object):
    def parse(self, task):
        newTasks = []
        ret, status = self.parseContent(task['__data'])
        meta = {}
        if status == 'OK':
            key = task['key']
            keyOutputPath = os.path.join(iPapa.iTsOutputPath, key)
            # contentMp3 
            if 'contentMp3' in ret:
                url = ret['contentMp3']
                dest = os.path.join(key, util.getUrlFileName(url)) 
                newT = Task(-1, url=url, handler='AudioHandler', taskType='media', ref=task.url, dest=dest)  
                newT['key'] = task['key']
                newT['audioType'] = os.path.splitext(dest)[1].upper()
                newTasks.append(newT)
            else:
                task.status = 'failed'
        else:
            task.status = 'failed'
        if newTasks != []:
            return {'newTasks': newTasks}
        return {}

    def parseContent(self, page):
        ret = {}
        soup = BS(page)
        try:
            li = soup.find('li', 'downloadlinkstatic') 
            src = li.a.get('href')
            ret['contentMp3'] = src
        except Exception, e:
            util.printException()
            return (None, e)

        return (ret, 'OK')


if __name__ == '__main__':
    data = open('tmp2').read()
    m = ContentMp3PageHandler()
    ret, status =  m.parseContent(data)
    for k in ret:
        print 'key', k
        print ret[k]

