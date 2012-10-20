#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web
from lib import BaseHandler, manager

class BoardHandler(BaseHandler):

    page_size = 15

    def get(self, boardname, rank=None):
        board = manager.board.get_board(boardname)
        if not board:
            raise tornado.web.HTTPError(404)
        boardname = board.boardname
        maxrank = max(0, manager.post.get_post_total(board['bid']))
        if rank is None:
            rank = maxrank // self.page_size * self.page_size
        else :
            rank = int(rank)
        posts = manager.post.get_posts(board['bid'], rank, self.page_size)
        if self.get_current_user() :
            userid = self.get_current_user()
            manager.readmark.wrapper_post_with_readmark(posts, boardname, userid)
            isfav = manager.favourite.is_fav(userid, board.bid)
        else:
            isfav = None            
        vistors = (
            ("LTaoist", "2012-03-04"),
            ("gcc", "2012-01-09"),
            ("cypress", "2012-01-01"),
            )
        board['bm'] = board['bm'] and board['bm'].split(':')
        board['httpbg'] = "http://ww3.sinaimg.cn/large/6b888227jw1dwesulldlyj.jpg"
        self.srender('board.html', board=board, rank=rank, maxrank=maxrank,
                     posts=posts, vistors=vistors, isfav=isfav,
                     page_size=self.page_size)

class APIQueryBoardHandler(BaseHandler):

    page_size = 15
    get_posts = manager.post.get_posts

    def get(self, boardname):
        res = manager.board.name_and_id(boardname)
        if res is None:
            self.write({
                    'success': False,
                    'content': u'没有该版块',
                    })
            return
        boardname = res.boardname
        bid = res.bid
        start = self.get_argument('start', None)
        if start is None or not start.isdigit():
            self.write({
                    "success": False,
                    "content": u'没有指定或错误的开始文章序号',
                    })
            return
        start = int(start)
        posts = self.get_posts(bid, start, self.page_size)
        for p in posts:
            p['posttime'] = p.posttime.isoformat()
        userid = self.get_current_user()
        if userid :
            manager.readmark.wrapper_post_with_readmark(posts,
                                                        boardname, userid)
        self.write({
                'success': True,
                'content': posts,
                })

class APIQueryGPostBoardHandler(APIQueryBoardHandler):

    get_posts = manager.post.get_posts_g

class APIQueryMPostBoardHandler(APIQueryBoardHandler):

    get_posts = manager.post.get_posts_m

class APIQueryTPostBoardHandler(APIQueryBoardHandler):

    get_posts = manager.post.get_posts_topic

class APIBookBoardHandler(BaseHandler):

    def get(self):
        userid = self.get_current_user()
        if userid is None:
            self.write({
                    "success": False,
                    "content": u"未登录用户.",
                    })
            return
        boardname = self.get_argument('boardname', None)
        print '(**', boardname
        board = boardname and boardname.isalpha() and \
            manager.board.get_board(boardname)
        if not board :
            self.write({
                    "success": False,
                    "content": u"没有该版块."
                    })
            return
        manager.favourite.add(userid, board.bid)
        return self.write({
                "success": True,
                "content": u"预定成功！",
                })
