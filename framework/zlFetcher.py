#!/usr/bin/env python
# -*- coding: utf-8 -*-  
import re
import urllib2
import urllib
import cookielib
import logging
import urlparse
from bs4 import BeautifulSoup as BS

import time
import os

import sys


global myLogger 
myLogger = None

if 'iPapa_worker' not in logging.Logger.manager.loggerDict:
    formatStr = ('%(asctime)s [%(levelname)s][%(filename)s:%(lineno)s]:'
                         ' %(message)s')
    logging.basicConfig(format=formatStr, level=logging.DEBUG)
    myLogger = logging.getLogger()
else:
    myLogger = logging.getLogger('iPapa_worker')


class Fetcher(object):
    def __init__(self, proxyName=None):
        """if force is True, do login"""
        self.proxyName = proxyName
        self.openerOK = self.installOpener(self.proxyName)
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/14.0.1',
                        'Referer':'','Content-Type':'application/x-www-form-urlencoded'}
    
    def installOpener(self, proxyName):
        # cookie
        myLogger.info("installOpener proxyName[%s]" % (proxyName))
        cj = None
        loaded = False
        opener = None
        proxy = None
        cj = cookielib.LWPCookieJar()
        cookie_processor = urllib2.HTTPCookieProcessor(cj)
        try:
            if proxyName != None and proxyName != '':
                proxy = urllib2.ProxyHandler({'http':proxyName})
                opener = urllib2.build_opener(cookie_processor, proxy, urllib2.HTTPHandler)
            else:
                opener = urllib2.build_opener(cookie_processor, urllib2.HTTPHandler)
        except Exception, e:
            myLogger.error("build opener failed[%s][cookie_filename:%s][proxyName:%s]" % (e, cookie_filename, proxyName))

        if opener != None:
            self.cj = cj
            self.opener = opener
            if proxyName != None and proxyName != '':
                self.proxyName = proxyName
                self.proxy = proxy
            myLogger.debug("installOpener OK proxyName[%s]" % (proxyName))
            return True  
        return False

    def switch(self, proxyName=None):
        """ """
        myLogger.debug("switch[proxyName=%s]" % (proxyName))
        self.openerOK = self.installOpener(self.proxyName) 
        if self.openerOK == False:
            return False
        return True

    def fetch(self, url, postdata={}, timeout=60):
        data = urllib.urlencode(postdata, True)
        try:
            if data != '':
                req = urllib2.Request(url, data=data, headers=self.headers)
            else:
                req = urllib2.Request(url, headers=self.headers)
            resp = self.opener.open(req, timeout=timeout)
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                myLogger.error('Reason: [%s] [%s]' % (e.reason, postdata))
                return (None, 'timeout')
            elif hasattr(e, 'code'):
                myLogger.error('Error code: [%s] [%s]' % (e.code, postdata))
                return (None, 'timeout')
            myLogger.error('failed [%s] in quering key word[%s]' % (e, postdata))    
        except Exception, e:
            myLogger.error('error[%s], url[%s] trace[%s]' % (e, postdata, 'not open'))
            return (None, 'timeout')
        return (resp, 'ok')

    def safeFetch(self, url, postdata={}, timeout=60):
        resp, status = self.fetch(url, postdata, timeout) 
        if resp == None:
            return None
        reUrl = resp.geturl().strip()
        if not self.theSameUrl(reUrl, url):
            return None
        return resp

    def theSameUrl(self, url1, url2):
        u1 = urlparse.urlsplit(url1)
        u2 = urlparse.urlsplit(url2)
        if u1.scheme+u1.netloc+u1.path ==\
            u2.scheme+u2.netloc+u2.path:
            return True
        return False

class zlFetcher(object):
    baseUrl = 'http://211.157.104.87:8080/sipo/zljs/hyjs-jieguo.jsp'
    detailBaseUrl = 'http://211.157.104.87:8080/sipo/zljs/'
    def __init__(self):
        self.f = Fetcher() 

    def combinePost(self, kw, recshu=20):
        """do login and store cookies in cookie_filename"""
        data = {
            'searchword': [(u'申请（专利权）人=(%s)' % kw).encode('GB2312')], 
            #'searchword': '',
            'textfield6':[(u'%s' % kw).encode('GB2312')],
            'recshu': [recshu],
            'flag3': [1],
            'pg': [1],
            'sign': [0],
        }
        return data


    def getPatentDetail(self, url):
        url = urlparse.urljoin(self.detailBaseUrl, url.encode('utf-8'))
        #logging.debug("url,"+url)
        page = self.fetch(url)
        #logging.debug("page"+page)
        detail = self.pickUpDetail(page.decode('gbk'))
        return detail


    def pickUpDetail(self, page):
        keys = (u'申请号', u'申请日', u'名称', u'公开(公告)号', \
                u'公开(公告)日', u'主分类号', u'申请(专利权)人')
        soup = BS(page)
        table = soup.find('table')
        trs = table.find_all('tr')
        detail = {}
        for tr in trs:
            lastField = None
            for td in tr.find_all('td'):
                if lastField != None:
                    detail[lastField] = td.text.strip()
                    lastField = None       
                else:
                    t = td.text      
                    t = re.sub(ur'\s+|\xa0', '', t)
                    t = t.strip(u'：')
                    if t in keys:
                        lastField = t
        return detail


    def getKwN(self, kw):
        data = self.combinePost(kw)
        page = self.read(data)
        n = self.pickUpN(page)
        return int(n)


    def getKwNUrl(self, kw, n):
        data = self.combinePost(kw, n+10)    
        page = self.read(data)
        urls = self.pickUpPageUrl(page)
        return urls

    
    def pickUpPageUrl(self, page):    
        ret = []
        soup = BS(page)       
        #print soup.text
        '''<tr onmouseover="this.className='td-over'" onmouseout="this.className='td-out'" class="td-out">'''
        trs = soup.find_all('tr', attrs={'onmouseout':'this.className=\'td-out\'', \
                                'onmouseover':"this.className='td-over'"})
        for tr in trs:
            tds = tr.find_all('td', attrs={'class':'dixian1'})
            zlId = tds[1].text.strip()    
            zlName = tds[2].text.strip()    
            url = (tds[2].a)['href']
            ret.append([zlId, zlName, url])
        return ret


    def pickUpN(self, page):
        if page == '' or page == None:
            return -1
        soup = BS(page)
        ''' <td height="23" align="right" bgcolor="#e9e9e9" class="zi"> '''
        td = soup.find(name='td', align='right', class_='zi')
        if td == None:
            return 0
        m = re.search(ur'共有(\d+)条记录', td.text)
        if m != None:
            return m.group(1)
        else:
            return -1


    def fetch(self, url):
        resp = self.f.safeFetch(url)
        data = ''
        if resp != None:
            try:
                data = resp.read()
            except Exception, e:
                logging.error('error[%s], data[%s]' % (e, data))
                data = '' 
        return data   


    def read(self, data):
        url = self.baseUrl
        resp = self.f.safeFetch(url, data)
        data = ''
        if resp != None:
            try:
                data = resp.read()
            except Exception, e:
                myLogger.error('error[%s], data[%s]' % (e, data))
                data = '' 
        return data
        

if __name__ == '__main__':
    f = zlFetcher()   
    myLogger.debug("ready")
    # tell me how many patents about this keyword
    n = f.getKwN(u'百度')
    if n < 0: #sth wrong
        sys.exit()
    # page = open('aa.html').read().decode('gb2312')
    # f.pickUpPageUrl(page)
    myLogger.debug("get kw n[%s]" %(n))
    # should be n in practice
    # ret =  f.getKwNUrl(u'百度', n)
    ret =  f.getKwNUrl(u'百度', 1)
    myLogger.debug("all baidu patent url got[%s]"%(len(ret)))

    for each in ret:
        print "%s\t%s\t%s" % (tuple(each))
        try:
            detail = f.getPatentDetail(each[2])        
            for k in detail:
                print k, detail[k].encode('utf-8')
        except Exception, e:
            logging.error("error here [%s]" % (e)) 

    logging.debug("ok all done")

