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
sys.path.insert(1, "../lib")
import util


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
                myLogger.error('Reason: [%s] [%s][%s]' % (e.reason, postdata, url))
                return (None, 'timeout')
            elif hasattr(e, 'code'):
                myLogger.error('Error code: [%s] [%s][%s]' % (e.code, postdata, url))
                return (None, 'timeout')
        except Exception, e:
            myLogger.error('error[%s], url[%s] trace[%s]' % (e, postdata, 'not open'))
            return (None, 'timeout')
        return (resp, 'OK')

    def safeFetch(self, url, postdata={}, timeout=60):
        """
            make sure there is no redirect
        """
        resp, status = self.fetch(url, postdata, timeout) 
        if resp == None:
            return None
        reUrl = resp.geturl().strip()
        if not self.theSameUrl(reUrl, url):
            return None
        return resp

    def keepFetchRead(self, url, postdata={}, timeout=60, times=3, safeFetch=True):
        ret = None
        while times!=0:
            if safeFetch == True:
                ret = self.safeFetch(url, postdata, timeout)
                if ret != None: # fetch ok
                    ret = self.read(ret)
                    if ret != None: # read ok
                        break
            else:
                ret, status = self.fetch(url, postdata, timeout)
                if status == 'OK': #fetch ok
                    ret = self.read(ret) 
                    if ret != None: # read ok
                        break
            times -= 1
        return ret

    def read(self, resp):
        ret = None 
        try:
            ret = resp.read()      
        except Exception, e:
            logging.error('error[%s], in read data' % (e))
            ret = None
        return ret


    def theSameUrl(self, url1, url2):
        u1 = urlparse.urlsplit(url1)
        u2 = urlparse.urlsplit(url2)
        if u1.scheme+u1.netloc+u1.path ==\
            u2.scheme+u2.netloc+u2.path:
            return True
        return False

    """
    def download(self, url, to, postdata={}, timeout=60, times=3, safeFetch=True):
        myLogger.info("fetcher download from [%s] to [%s]" % (url, to))
        ret = None
        while times!=0:
            status=''
            if safeFetch == True:
                resp = self.safeFetch(url, postdata, timeout)
            else:
                resp, status = self.fetch(url, postdata, timeout)

            if util.mkdir(os.path.dirname(to)) == False:
                times -= 1
                ret = None
                continue

            if status == 'OK' or (status == '' and resp != None): # fetch ok
                #CHUNK = 512 * 1024
                with open(to, 'wb') as f:
                    ret = True
                    try:
                        chunk = resp.read()
                        f.write(chunk)
                    except Exception, e:
                        msg = util.exprException()
                        util.printException()
                        ret = None

                if ret == True:
                    break
            times -= 1
        return ret
    """


    def download(self, url, to, postdata={}, timeout=60, times=3, safeFetch=True):
        myLogger.info("fetcher download from [%s] to [%s]" % (url, to))
        ret = None
        while times!=0:
            status=''
            if safeFetch == True:
                resp = self.safeFetch(url, postdata, timeout)
            else:
                resp, status = self.fetch(url, postdata, timeout)

            if util.mkdir(os.path.dirname(to)) == False:
                times -= 1
                ret = None
                continue

            if status == 'OK' or (status == '' and resp != None): # fetch ok
                CHUNK = 1024 * 1024 * 5
                with open(to, 'wb') as f:
                    ret = True
                    try:
                        while True:
                            chunk = resp.read(CHUNK)
                            if not chunk: 
                                break
                            f.write(chunk)
                    except Exception, e:
                        msg = util.exprException()
                        util.printException()
                        ret = None

                if ret == True:
                    break
            times -= 1
        return ret

if __name__ == '__main__':
    f = Fetcher()
    url = "http://av.voanews.com/clips/LERE/2014/08/27/8845a541-a3b2-4539-a417-6f6644edd222.mp3?download=1"
    print f.download(url, "./here.mp3")
    #def download(self, url, to, postdata={}, timeout=60, times=3, safeFetch=True):
