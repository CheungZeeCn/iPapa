#/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-24 21:07:29 
# Copyright 2014 NONE rights reserved.

from setup import iPapa
from bs4 import BeautifulSoup as BS
from iTask import Task
import urlparse
import os
import util

class ClassPageHandler(object):
    def __init__(self):
        self.historyKeys = set([])
        self.__init__historyKeys()

    def __init__historyKeys(self):
        files = os.listdir(iPapa.iDataPath)        
        for f in files:
            if f.startswith('klist.'):
                with open(os.path.join(iPapa.iDataPath, f)) as ff:
                    for k in ff:
                        self.historyKeys.add(k.strip())
        return True

    def parse(self, task):
        newTasks = []
        ret, status = self.parseContent(task['__data'])
        if status == 'OK':
            for k in ret['zipPic']:
                if k not in self.historyKeys:
                    dest = os.path.join(k, os.path.basename(ret['zipPic'][k]))
                    newT = Task(-1, url=ret['zipPic'][k], handler='PicHandler', ref=task.url, taskType='media', dest=dest)  
                    newT['key'] = k
                    newT['picType'] = 'zipPic'
                    newTasks.append(newT)
            
            for k in ret['contentPage']:
                if k not in self.historyKeys:
                    newT = Task(-1, url=urlparse.urljoin(task.url, ret['contentPage'][k]), handler='ContentPageHandler', ref=task.url)  
                    newT['key'] = k
                    newTasks.append(newT)
        if newTasks != []:
            return {'newTasks': newTasks}
        return {}

    def parseContent(self, page):
        ret = {'zipPic':{}, 'contentPage':{}}
        try:
            soup = BS(page)           
            titleDiv = soup.find(id='archive').h2  
            classTitle = titleDiv.text
            #ul = soup.find('ul', "bullet_orange")
            divs = soup.find_all('div', 'archive_rowmm')
            for div in divs:
                zipPic = div.img.get('src')
                #has audio?
                a = div.h4.a
                if a.select('span.assignedIcon.asIcoAudio') != []:
                    span = a.find('span', 'underlineLink')
                    url = a.get('href')
                    key = url.replace('/', '_')
                    ret['zipPic'][key] = zipPic
                    ret['contentPage'][key] = url
        except Exception, e:
            util.printException()
            return (None, e)

        return (ret, 'OK')


if __name__ == '__main__':
    import sys
    inputCase = sys.argv[1]
    data = open(inputCase).read()
    m = ClassPageHandler()
    ret, status =  m.parseContent(data)

