#!/usr/bin/python2
# -*- coding: utf-8 -*-

import tornado
import tornado.web

from lib import BaseHandler, manager

class IndexHandler(BaseHandler):

    def get(self):
        billboard = manager.web.get_billboard()
        topten = manager.web.get_topten()
        boardnav = manager.web.get_board_nav()
        news = manager.web.get_news()
        self.srender("index.html", billboard=billboard,
                     topten=topten, boardnav=boardnav,
                     news=news)

class LoginHandler(BaseHandler):

    def post(self):
        try:
            userid = manager.auth.login_http(
                self.get_argument("userid"),
                self.get_argument("passwd"),
                self.request.remote_ip,
                )
        except Exception as e:
            self.write(e.message)
            self.finish()
        else:
            #print repr(userid)
            self.set_secure_cookie('userid', userid)
            self.redirect('/')

class LogoutHandler(BaseHandler):

    def get(self):
        self.clear_cookie('userid')
        self.redirect('/')

class ErrorHandler(BaseHandler):
    
    """Generates an error response with status_code for all requests."""
    def __init__(self, application, request, status_code):
        tornado.web.RequestHandler.__init__(self, application, request)
        self.set_status(status_code)
    
    def prepare(self):
        raise tornado.web.HTTPError(self._status_code)

## override the tornado.web.ErrorHandler with our default ErrorHandler
tornado.web.ErrorHandler = ErrorHandler
