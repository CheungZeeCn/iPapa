#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-24 21:07:29 
# Copyright 2014 NONE rights reserved.

import setup
from setup import iPapa

from bs4 import BeautifulSoup as BS
from iTask import Task
import os
import urlparse
import util

class IndexPageHandler(object):
    def parse(self, task):
        output = {}
        ret, status = self.parseContent(task['__data'])
        if status != 'OK':
            task.status = 'failed'
            return output
            
        output['newTasks'] = []
        for link in ret:
            # add pc10 to get more articles here
            newT = Task(-1, url=urlparse.urljoin(task.url, link), handler='ClassPageHandler', ref=task.url)  
            output['newTasks'].append(newT) 
        return output

    def parseContent(self, page):
        ret = []
        try:
            soup = BS(page)           
            headerDiv = soup.find(id='indexItems')  
            headlis = headerDiv.select('li')
            for li in headlis:
                iUrl = urlparse.urljoin(li.a['href'].rstrip(".html")+"/", "pc10.html?tab=None")
                #iUrl = urlparse.urljoin(li.a['href'].rstrip(".html")+"/", "pc0.html?tab=None")
                ret.append(iUrl)

        except Exception, e:
            util.printException()
            return (None, e)
    
        return (ret, 'OK')


if __name__ == '__main__':
    data = open('cases/programindex.html').read()
    m = IndexPageHandler()
    print m.parseContent(data)

