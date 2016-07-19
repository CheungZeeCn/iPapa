#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-08-24 21:07:29 
# Copyright 2014 NONE rights reserved.

"""
Modified by zhangzhi for new VOA page version 
                    @2016-07-19
"""

from setup import iPapa
from datetime import datetime
from bs4 import BeautifulSoup as BS
import os
import urlparse
from iTask import Task
import util
import re
import logging

class ContentPageHandler(object):
    def __init__(self):
        self.reXHX = re.compile(r"(%s)_+"%"_"*12)

    def parse(self, task):
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
            siteTitleDiv = soup.find('div', 'category')
            ret['siteTitle'] = siteTitleDiv.a.text

            titleH1 = soup.find('div', 'col-title').find('h1')
            ret['title'] = titleH1.text.strip()

            pubTime = ''
            try:
                pubTimeTxt = soup.find('div', 'publishing-details').span.time['datetime']
                #7/18/2016 9:05:13 PM
                #datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')  
                pubTime = datetime.strptime(pubTimeTxt, '%m/%d/%Y %I:%M:%S %p').strftime("%Y-%m-%d %H:%M:%S")  
                ret['date'] = pubTime
            except Exception, e:
                pass
            
            # contentPic 
            imgs = soup.select('.col-multimedia > .media-placeholder.image img')
            if imgs != []:
                ret['contentPics'].append(imgs[0].get('src'))    
            paras = soup.select('.col-multimedia > .media-placeholder.image p.caption')
            if paras != []:
                ret['contentPicCaptions'] = paras[0].text   

            #print ret
            #return 0, {}     

            linkFound = False

            if linkFound == False:
                divDownload = soup.find('div', 'media-download')    
                links = divDownload.select('li.subitem > a')
                reNum = re.compile(r'\d+')
                if links != []:
                    minA = links[0]
                    minKbps = int(reNum.search(minA.text.strip()).group())
                    for a in links:
                        aKbps = int(reNum.search(a.text.strip()).group())
                        if aKbps < minKbps:
                            minA = a
                            minKbps = aKbps
                    ret['contentMp3'] = minA.get('href')
                    linkFound = True

            #if linkFound == False
            #    li = soup.find('li', 'downloadlinkstatic') 
            #    if li != None:
            #        src = li.a.get('href')
            #        ret['contentMp3'] = src
            #        linkFound = True



            #if linkFound == False:
            #    li = soup.find('li', 'listenlink')
            #    if li != None:
            #        url = li.a.get('href')
            #        # be careful here !!! contentMp3Page is not the same with contentMp3
            #        ret['contentMp3Page'] = url
            #        linkFound = True

            #if linkFound == False:
            #    li = soup.find('li', 'downloadlink')
            #    if li != None:
            #        url = li.a.get('href')
            #        ret['contentMp3'] = url
            #        linkFound = True

            contentDiv = soup.find('div', 'wysiwyg') 

            contentZoomMeDiv = contentDiv

            mp3Div = contentZoomMeDiv.find('div', 'player-and-links')
            if mp3Div:
                mp3Div.decompose()    

            #delete mp3 player part
            mp3H5 = contentZoomMeDiv.find('h5', 'tagaudiotitle')
            if mp3H5:
                #print mp3H5
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
                                if tag.find_next_sibling('h5', 'tagaudiotitle') or \
                                        tag.find_next_sibling('div', ['mediaplayer', 'audioplayer']):
                                    keepDelete = True
                                    tag.decompose()

                                #if  tag.find('span') and self.reXHX.search(tag.span.text):
                                #    print tag
                                #    #keepDelete = True
                                #    #tag.span.decompose()

                                #elif tag.find('em') and self.reXHX.search(tag.em.text):
                                #    print tag
                                #    #keepDelete = True
                                #    #tag.em.decompose()

                                #elif self.reXHX.search(tag.text):
                                #    print tag
                                #    #keepDelete = True
                                #    #tag.decompose()
                            
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
                                #print tag
                                #keepDelete = True
                                #tag.span.decompose()
                                if tag.find_next_sibling('h5', 'tagaudiotitle') or \
                                        tag.find_next_sibling('div', ['mediaplayer', 'audioplayer']):
                                    keepDelete = True
                                    tag.decompose()

                            elif tag.find('em') and self.reXHX.search(tag.em.text):
                                #print tag
                                #keepDelete = True
                                #tag.em.decompose()
                                if tag.find_next_sibling('h5', 'tagaudiotitle') or \
                                        tag.find_next_sibling('div', ['mediaplayer', 'audioplayer']):
                                    keepDelete = True
                                    tag.decompose()

                            elif self.reXHX.search(tag.text):
                                #print tag
                                #keepDelete = True
                                #tag.decompose()
                                if tag.find_next_sibling('h5', 'tagaudiotitle') or \
                                        tag.find_next_sibling('div', ['mediaplayer', 'audioplayer']):
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

                if tag.name == 'img':
                    embImg = tag
                    src = embImg.get('src')
                    ret['embPics'].append(src)
                    newSrc = os.path.basename(urlparse.urlparse(src).path)
                    embImg['src'] = newSrc
                    tag.replace_with(embImg)
                
            ret['content'] = "%s" % contentZoomMeDiv.prettify().encode('utf-8')
        except Exception, e:
            util.printException()
            return (None, e)

        return (ret, 'OK')


if __name__ == '__main__':
    data = open("cases/contentPage.html").read()
    m = ContentPageHandler()
    ret, status =  m.parseContent(data)
    #if ret == None:
    #    print "None"
    #else:
    #    for k in ret:
    #        print k, ret[k]
    #    
    print ret['content']

