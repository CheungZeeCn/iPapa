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
import re

class ContentPageHandler(object):
    def __init__(self):
        self.reXHX = re.compile(r"(%s)_+"%"_"*12)

    def parse(self, task):
        print "ContentPageHandler parse", task.url, task['key']
        newTasks = []
        ret, status = self.parseContent(task['__data'])
        meta = {}
        if status == 'OK':
            key = task['key']
            keyOutputPath = os.path.join(iPapa.iTsOutputPath, key)
            #siteTile 
            meta['siteTitle'] = ret['siteTitle']
            #title
            meta['title'] = ret['title']
            # url
            meta['url'] = task.url
            # date
            meta['date'] = ret['date']
            #contentPics
            #record and new task to download it
            meta['contentPics'] = ret['contentPics']
            meta['contentPicCaptions'] = ret['contentPicCaptions']
            meta['embPics'] = ret['embPics']
            #create new tasks here
            if len(ret['contentPics']) and len(ret['contentPicCaptions']):
                picUrl = ret['contentPics'][0]
                #only the first pic here, ignore others now
                dest = os.path.join(key, util.getUrlFileName(picUrl)) 
                newT = Task(-1, url=picUrl, handler='PicHandler', taskType='media', ref=task.url, dest=dest)  
                newT['key'] = task['key']
                newT['picType'] = 'contentPic'
                newTasks.append(newT)

            #for content, we store it 
            contentLoc = os.path.join(keyOutputPath, 'content.html')
            util.writeFile(contentLoc, ret['content'])
            # contentMp3 
            if 'contentMp3' in ret:
                url = ret['contentMp3']
                dest = os.path.join(key, util.getUrlFileName(url)) 
                newT = Task(-1, url=url, handler='AudioHandler', taskType='media', ref=task.url, dest=dest)  
                newT['key'] = task['key']
                newT['audioType'] = os.path.splitext(dest)[1].upper()
                newTasks.append(newT)
            elif 'contentMp3Page' in ret: #always be with big file, we ignore it 
                #url = ret['contentMp3Page']
                #newT = Task(-1, url=urlparse.urljoin(task.url, url), handler='ContentMp3PageHandler', ref=task.url,) 
                #newT['key'] = task['key']
                #newTasks.append(newT)
                task.status = 'ignore' 
                meta['isIgnore'] = True
                meta['ignoreMsg'] = "Audio file is too big, we should ignore this now."
                task.msg = 'Audio file is too big, we should ignore this now.' 
            else:
                #Failed
                task.status = 'failed' 
                task.msg = 'failed in Findding a Audio' 

            # download here 
            # embPics
            for embPic in ret['embPics']:
                picUrl = embPic
                #only the first pic here, ignore others now
                dest = os.path.join(key, util.getUrlFileName(picUrl)) 
                newT = Task(-1, url=picUrl, handler='PicHandler', taskType='media', ref=task.url, dest=dest)  
                newT['key'] = task['key']
                newT['picType'] = 'embPic'
                newTasks.append(newT)

            # store meta file
            metaLoc = os.path.join(keyOutputPath, 'meta.json') 
            if util.dump2JsonFile(meta, metaLoc) != True:
                task.status = 'failed'    

        else:
            task.status = 'failed'
        if task.status == 'ignore': 
            return {}
        if newTasks != []:
            return {'newTasks': newTasks}
        return {}

    def parseContent(self, page):
        ret = {'contentPics':[], 'contentPicCaptions':[], 'embPics':[]}
        try:
            soup = BS(page)           
            articleDiv = soup.find('div', id='article') 
            siteTitleH2 = articleDiv.find('h2', 'sitetitle')
            ret['siteTitle'] = siteTitleH2.a.text

            titleH1 = articleDiv.find('h1')
            ret['title'] = titleH1.text.strip()

            picDiv = soup.find('div', 'watermark')
            if picDiv and picDiv.parent['class'] == ['contentImage', 'floatNone']:
                ret['contentPics'].append(picDiv.a.img.get('src'))
                ret['contentPicCaptions'].append(picDiv.next_sibling.text)

            li = soup.find('li', 'downloadlinkstatic') 
            if li != None:
                src = li.a.get('href')
                ret['contentMp3'] = src
            else:
                li = soup.find('li', 'listenlink')
                url = li.a.get('href')
                ret['contentMp3Page'] = url
                              
            contentDiv = articleDiv.find('div', 'articleContent') 
            dateDiv = contentDiv.find('div', 'dateblock')
            date = dateDiv.text.strip()
            ret['date'] = date
            
            contentZoomMeDiv = contentDiv.find('div', 'zoomMe') 
            #delete mp3 player part
            mp3H5 = contentZoomMeDiv.find('h5', 'tagaudiotitle')
            if mp3H5:
                print mp3H5
                div = mp3H5.find_next_sibling('div', 'mediaplayer audioplayer')   
                div.decompose()
                mp3H5.decompose()

            #delete script
            for ele in contentZoomMeDiv.find_all('script'):
                ele.decompose()
            
            for ul in contentZoomMeDiv.find_all('ul'):
                if ul.find('li', 'playlistlink') or \
                    ul.find('li', 'listenlink'):
                        ul.decompose()

            #print contentZoomMeDiv
            #delete until first p
            if contentZoomMeDiv.find('div', 'wordclick'):
                iterContent = contentZoomMeDiv.find('div', 'wordclick')
            else:
                iterContent = contentZoomMeDiv

            for tag in iterContent.find_all():
                if tag.name != None:
                    if tag.name != 'p' and tag.name != 'br':
                        tag.decompose()
                    else:
                        break
            
            keepDelete = False
            for tag in iterContent.find_all():
                if tag.name != None:
                    if keepDelete == False:
                        if tag.name == 'div':
                            tagClass = tag.get('class')
                            if tag.find('p') and self.reXHX.search(tag.p.text):
                                oriTag = tag
                                tag =  tag.p
                                #check em
                                keepDelete = True
                                tag.decompose()
                                if  tag.find('span') and self.reXHX.search(tag.span.text):
                                    print tag
                                    keepDelete = True
                                    tag.span.decompose()

                                elif tag.find('em') and self.reXHX.search(tag.em.text):
                                    print tag
                                    keepDelete = True
                                    tag.em.decompose()

                                elif self.reXHX.search(tag.text):
                                    print tag
                                    keepDelete = True
                                    tag.decompose()
                            
                            elif tagClass:
                                if 'infgraphicsAttach' in tagClass:
                                    tag.decompose()
                                if 'boxwidget' in tagClass:
                                    #boxwidget w_Quiz2c w_QuizInside
                                    tag.decompose()
                        elif tag.name == 'iframe':
                            tag.decompose()

                        elif tag.name == 'p':
                            #check em
                            if  tag.find('span') and self.reXHX.search(tag.span.text):
                                print tag
                                keepDelete = True
                                tag.span.decompose()

                            elif tag.find('em') and self.reXHX.search(tag.em.text):
                                print tag
                                keepDelete = True
                                tag.em.decompose()

                            elif self.reXHX.search(tag.text):
                                print tag
                                keepDelete = True
                                tag.decompose()
                                  
                    else:
                        tag.decompose()

            #print contentZoomMeDiv
            #filt photos in content
            for tag in iterContent.find_all():
                if tag.name == 'div' and tag.get('class'):
                    if 'embedded_content_object' in tag.get('class'):
                        embDiv = tag 
                        embImgDiv = embDiv.find('div', 'contentImage')
                        if embImgDiv:
                            embImg = embImgDiv.find('img')
                            src = embImg.get('src')
                            ret['embPics'].append(src)
                            newSrc = os.path.basename(urlparse.urlparse(src).path)
                            embImg['src'] = newSrc
                            tag.replace_with(embImgDiv)
                        else:
                            tag.decompose()
                
            ret['content'] = "%s" % contentZoomMeDiv.prettify().encode('utf-8')
            
        except Exception, e:
            util.printException()
            return (None, e)

        return (ret, 'OK')


if __name__ == '__main__':
    data = open('tmp3').read()
    m = ContentPageHandler()
    ret, status =  m.parseContent(data)
    for k in ret:
        print 'key', k
        print ret[k]

