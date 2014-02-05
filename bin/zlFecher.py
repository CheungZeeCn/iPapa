#!/usr/bin/env python
# -*- coding: utf-8 -*-  
import re
import urllib2
import urllib
import cookielib
import traceback
import socket
import logging
from bs4 import BeautifulSoup as BS

formatStr = ('%(asctime)s [%(levelname)s][%(filename)s:%(lineno)s]:'
                     ' %(message)s')
logging.basicConfig(format=formatStr, level=logging.DEBUG)
import time
import os
import lxml.html as HTML
import urlparse


class Fetcher(object):
    def __init__(self, proxyName=None):
        """if force is True, do login"""
        self.proxyName = proxyName
        self.openerOK = self.installOpener(self.proxyName)
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/14.0.1',
                        'Referer':'','Content-Type':'application/x-www-form-urlencoded'}
    
    def installOpener(self, proxyName):
        # cookie
        logging.info("installOpener proxyName[%s]" % (proxyName))
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
            logging.error("build opener failed[%s][cookie_filename:%s][proxyName:%s]" % (e, cookie_filename, proxyName))

        if opener != None:
            self.cj = cj
            self.opener = opener
            if proxyName != None and proxyName != '':
                self.proxyName = proxyName
                self.proxy = proxy
            logging.debug("installOpener OK proxyName[%s]" % (proxyName))
            return True  
        return False

    def switch(self, proxyName=None):
        """ """
        logging.debug("switch[proxyName=%s]" % (proxyName))
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
                logging.error('Reason: [%s] [%s]' % (e.reason, postdata))
                return (None, 'timeout')
            elif hasattr(e, 'code'):
                logging.error('Error code: [%s] [%s]' % (e.code, postdata))
                return (None, 'timeout')
            logging.error('failed [%s] in quering key word[%s]' % (e, postdata))    
        except Exception, e:
            logging.error('error[%s], url[%s] trace[%s]' % (e, postdata, 'not open'))
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

    def getKwN(self, kw):
        data = self.combinePost(kw)
        page = self.read(data)
        n = self.pickUpN(page)
        return n

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
        soup = BS(page)
        ''' <td height="23" align="right" bgcolor="#e9e9e9" class="zi"> '''
        td = soup.find(name='td', align='right', class_='zi')
        if td == None:
            return 0
        m = re.search(ur'共有(\d+)条记录', td.text)
        if m != None:
            return m.group(1)
        else:
            return 0


    def read(self, data):
        url = self.baseUrl
        resp = self.f.safeFetch(url, data)
        data = ''
        if resp != None:
            try:
                data = resp.read()
            except Exception, e:
                logging.error('error[%s], data[%s]' % (e, data))
                data = '' 
        return data
        

if __name__ == '__main__':
    f= zlFetcher()   
    #n = f.getKwN(u'百度')
    #page = open('aa.html').read().decode('gb2312')
    #f.pickUpPageUrl(page)
    ret =  f.getKwNUrl(u'百度', 1)
    for each in ret:
        print "%s\t%s\t%s" % (tuple(each))


