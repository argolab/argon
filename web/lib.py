# -*- coding: utf-8 -*-
#!/usr/bin/env python

import sys
sys.path.append('..')

from argo_conf import *

'''
   argon.web.lib
   ~~~~~~~~~~~~~

   Some common function and base.

'''

from model import manager
from model import manager as mgr
from datetime import datetime
import httplib
import tornado
import traceback

class SDict(dict):
    """A dict that allows for object-like property access syntax."""
    def __getattr__(self, name):
        return self[name]

def url_for_avatar(userid):
    '''
    Return the avatar url for userid.
    NOT IMPLEMENTED YET.
    '''
    return manager.userinfo.get_avatar(userid) or "/static/img/avatar_default.jpg"

def shorttime(time):
    '''
    Better and short outlook for time.
    '''
    return time.strftime('%d-%m')


func = SDict([
    ("url_for_avatar", url_for_avatar),
    ('shorttime', shorttime),
    ])

class BaseHandler(tornado.web.RequestHandler):

    '''The BaseHandler for all handler.'''

    @property
    def db(self):
        return self.application.db

    @property
    def ch(self):
        return self.application.ch

    @property
    def headers(self):
        return self.application.headers

    @property
    def userid(self):
        return self.get_secure_cookie('userid')

    def prepare(self):
        self.escape = tornado.escape
        self.remote_ip = self.request.remote_ip

    def get_current_user(self):
        return self.get_secure_cookie('userid')

    def srender(self, tpl, **kwargs):
        '''Wrap func into template namespace.'''
        self.render(tpl, func=func, **kwargs)

    def get_error_html(self, status_code, **kwargs):
        if status_code == 404:
            self.write(self.render_string('404.html'))
            return
        if self.settings.get("debug") and 'exc_info' in kwargs :
            # in debug mode, try to send a traceback
            self.set_header('Content-Type', 'text/plain')
            for line in traceback.format_exception(*kwargs["exc_info"]):
                self.write(line)
            self.write()
        else:
            self.write("<html><title>%(code)d: %(message)s</title>"
                        "<body>%(code)d: %(message)s</body></html>" % {
                    "code": status_code,
                    "message": httplib.responses[status_code],
                    })

class BaseFileHandler(BaseHandler, tornado.web.StaticFileHandler):
    pass

def import_handler(modulename, classname):
    '''
    Import a class from the module, and return it.
    It common use to setting the urls in server.py.
    '''
    module = __import__(name=modulename, fromlist=classname, level=0)
    return getattr(module, classname)

def bid_wrapper(userid):
    '''
    Wrapper the bid as a board object, with the read status of userid.
    '''
    def wrapper(bid):
        board = manager.board.get_board_by_id(bid)
        board['is_new'] = manager.readmark.is_new_board(userid, bid,
                                                        board.boardname)
        return board
    return wrapper

def timeformat(time):
    '''
    Better outlook for time.
    '''
    return time.strftime("%d-%m")

def fun_gen_quote(userid, content):
    '''
    Wrapper the content by userid to be quote.
    '''    
    max_quote_line = 5

    owner = mgr.userinfo.get_user(userid)
    print '************************'
    print owner
    if not owner:
        owner = {}
        owner['userid'] = owner['username'] = 'null' 

    pattern = u'\n\n【 在 %s ( %s ) 的大作中提到: 】' % \
                ( owner['userid'], owner['username'] )

    quote = pattern + '\n' + '\n'.join(map(lambda l: u':'+l, content.split('\n')[:max_quote_line]))

    return quote


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
