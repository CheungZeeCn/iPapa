#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# by zhangzhi @2014-02-03 19:57:22 
# Copyright 2014 NONE rights reserved.

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import logging
import util
import json
import threading
import time

myLogger = None
if 'iPapa_controller' not in logging.Logger.manager.loggerDict:
    myLogger = logging.getLogger()
else:
    myLogger = logging.getLogger('iPapa_controller')



class HTTPWatchServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, watchHandler=None):
        HTTPServer.__init__(self, server_address, RequestHandlerClass)
        self.watchHandler = watchHandler
        myLogger.debug('HTTPWatchServer initialization done')

class WatchRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        myLogger.info("%s - - [%s]" %
                         (self.address_string(),
                          format%args))
    def do_GET(self):
        """
            do_GET in v 0.1
            Asking status ONLY
                11. How many threads
                12. The status for each threads, timestamp or \
                    something like that
                13. The leangths for inQueue and outQueue
                14. The running times(duration, timeBegin...).
        """
        self.protocal_version = 'HTTP/1.1'
        self.send_response(200)  
        self.send_header("Welcome", "iPaPa Console v0.1, mua~")         
        self.end_headers()
        report = {}

        m = self.server.watchHandler
        report = m.genStatus()
        # simple at first, no router now
        buf = '%s' % (json.dumps(report))
        # how many all tasks done
        #
        self.wfile.write(buf)  

def run(server_class=HTTPWatchServer,
        handler_class=WatchRequestHandler, port=28282, m=999):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class, m)
    httpd.serve_forever()

if __name__ == '__main__':
    run()

