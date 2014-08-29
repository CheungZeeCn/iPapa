#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-24 21:07:29 
# Copyright 2014 NONE rights reserved.

from bs4 import BeautifulSoup as BS
from iTask import Task
import os
import urlparse
import util

class MainPageHandler(object):
    def parse(self, task):
        output = {}
        ret, status = self.parseContent(task['__data'])
        if status != 'OK':
            task.status = 'failed'
            return output
            
        output['newTasks'] = []
        for link in ret:
            newT = Task(-1, url=urlparse.urljoin(task.url, link), handler='ClassPageHandler', ref=task.url)  
            output['newTasks'].append(newT) 
        return output

    def parseContent(self, page):
        ret = []
        try:
            soup = BS(page)           
            headerDiv = soup.find(id='header')  
            headlis = headerDiv.select('li.header_navigation_item.has_child')
            for li in headlis:
                if li.a.text == 'Audio':
                    links = li.find_all('a', 'section_link')
                    break
            for link in links:
                ret.append(link['href'])

        except Exception, e:
            util.printException()
            return (None, e)
    
        return (ret, 'OK')


if __name__ == '__main__':
    data = open('tmp').read()
    m = MainPageHandler()
    m.parserContent(data)

