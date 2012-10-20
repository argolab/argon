#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')
import os
import tornado
import tornado.ioloop
import tornado.web
import tornado.httpserver
from model import globaldb
from lib import import_handler
import uimodules

class Application(tornado.web.Application):

    def __init__(self, handlers, **settings):
        '''Simply bind bd and ch to the application.'''
        tornado.web.Application.__init__(self, handlers, **settings)
        # set db and cache here
        self.db = globaldb.global_conn
        self.ch = globaldb.global_cache

urls = [

    (r"/", import_handler("index", "IndexHandler")),
    (r"/account/login", import_handler("index", "LoginHandler")),
    (r'/account/logout', import_handler('index', 'LogoutHandler')),
    (r'/board/(\w{1,40})/(\d{1,10})?', import_handler('board', 'BoardHandler')),
    (r'/post/(\d{1,20})', import_handler('post', 'PostHandler')),
    (r'/post/reply/(\d{1,20})', import_handler('post', 'ReplyPostHandler')),
    (r'/post/add/(\w{1,40})', import_handler('post', 'NewPostHandler')),
    (r'/notify', import_handler('user', 'NoticeHandler')),
    (r'/user/(\w{1,40})', import_handler('user', 'UserInfoHandler')),

    (r'/mail', import_handler('mail', 'MailHandler')),

    (r'/api/get_posts/(\w{2,16})', import_handler('board', 'APIQueryBoardHandler')),
    (r'/api/get_post', import_handler('post', 'APIGetPostHandler')),
    (r'/api/get_posts_g/(\w{2,16})', import_handler('board', 'APIQueryGPostBoardHandler')),
    (r'/api/get_posts_m/(\w{2,16})', import_handler('board', 'APIQueryMPostBoardHandler')),
    (r'/api/get_posts_t/(\w{2,16})', import_handler('board', 'APIQueryTPostBoardHandler')),
    (r'/api/book_board', import_handler("board", "APIBookBoardHandler")),
    (r'/api/new_post', import_handler('post', 'APINewPostHandler')),
    (r'/api/reply_post/(\d{1,4})', import_handler('post', 'APIReplyPostHandler')),

    (r'/a/get_maillist/(\d{1,4})?', import_handler('mail','AjaxMailListHandler')),
    (r'/a/get_mail/(\d{1,4})', import_handler('mail', 'AjaxGetMailHandler')),
    (r'/a/add_mail', import_handler('mail', 'AjaxAddMailHandler')),
    (r'/a/reply_mail/(\d{1,4})', import_handler('mail', 'AjaxReplyMailHandler')),
    
    (r"/a/checkmail/?", import_handler("comm_ajax","CommAjaxCheckMailHandler")),
    (r"/a/mail/(\d{1,10})/?", import_handler("comm_ajax","CommAjaxGetMailHandler")),
    (r"/a/board/(\d{1,2})/?", import_handler("comm_ajax","CommAjaxGetBoardHandler")),
    (r"/a/(\w{2,16})/(\d{1,10})/?", import_handler("comm_ajax","CommAjaxGetPostHandler")),
    (r"/a/(\w{2,16})/quote/(\d{1,10})/?", import_handler("comm_ajax","CommAjaxGetQuoteHandler")),
    (r"/a/(\w{2,16})/post/?", import_handler("comm_ajax", "CommAjaxNewPostHandler")),
    (r"/avatar/(\w{2,16})", import_handler("user", "UserAvatarHandler"),
     { "path": os.path.join(os.path.dirname(__file__), "attach") }),

    # mobile
    (r"/m/?$", import_handler("mobile.m_main","MobileIndexHandler")),
    (r"/m/login/?$", import_handler("mobile.m_main","MobileLoginHandler")),
    (r"/m/logout/?$", import_handler("mobile.m_main","MobileLogoutHandler")),
    (r"/m/brds/?$", import_handler("mobile.m_main","MobileBoardHandler")),
    (r"/m/data/?$", import_handler("mobile.m_main","MobileDataHandler")),
    (r"/m/about/?$", import_handler("mobile.m_main","MobileAboutHandler")),
    (r"/m/fav/?$", import_handler("mobile.m_main","MobileFavHandler")),
    (r"/m/mail/?(-?\d{1,10})?/?$", import_handler("mobile.m_main","MobileMailHandler")),
    (r"/m/mail/send/(\d{1,10})?/?$", import_handler("mobile.m_main","MobileSendMailHandler")),

    (r"/m/(\w{2,16})/?(-?\d{1,10})?/?", import_handler("mobile.m_main","MobilePostHandler")),
    (r"/m/(\w{2,16})/post/?", import_handler("mobile.m_main","MobileNewPostHandler")),
    (r"/m/(\w{2,16})/thread/(\d{1,10})/?", import_handler("mobile.m_main","MobileThreadHandler")),


    # (r"/404", import_handler('index', 'NotPageHandler'))
    # (r"/post/(\d{1,10})", import_handler("post", "PostHandler")),
    # (r"(
    ]

settings = dict (
    template_path=os.path.join(os.path.dirname(__file__), "template"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    # xsrf_cookies=True,
    cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    autoescape='xhtml_escape',
    ui_modules=uimodules,
    debug=True,
    )

def main():
    application = Application(urls, **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8080)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
