#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web
from lib import BaseHandler, manager, fun_gen_quote

class APIGetPostHandler(BaseHandler):

    def get(self):
        pid = self.get_argument('pid', None)
        if not pid:
            self.write({
                    'success': False,
                    'content': '错误的帖子id',
                    })
            return
        post = manager.post.get_post(pid)
        if not post:
            self.write({
                    'success': False,
                    'content': '没有该帖子',
                    })
            return
        board = manager.board.get_board_by_id(post['bid'])
        if self.get_current_user() :
            userid = self.get_current_user()
            manager.readmark.set_read(userid, board.boardname, pid)
        post['posttime'] = post.posttime.isoformat()
        prevpid = manager.post.prev_post_pid(post.bid, post.pid)
        nextpid = manager.post.next_post_pid(post.bid, post.pid)
        self.write({
                'success': True,
                'post': post,
                'prevpid': prevpid,
                'nextpid': nextpid,
                });

class PostHandler(BaseHandler):

    def get(self, pid):
        print self.request
        if not pid:
            raise tornado.web.HTTPError(404)
        post = manager.post.get_post(pid)
        if not post:
            raise tornado.web.HTTPError(404)
        board = manager.board.get_board_by_id(post['bid'])
        if self.get_current_user() :
            userid = self.get_current_user()
            manager.readmark.set_read(userid, board.boardname, pid)
        post['posttime'] = post.posttime.isoformat()
        prevpid = manager.post.prev_post_pid(post.bid, post.pid)
        nextpid = manager.post.next_post_pid(post.bid, post.pid)
        self.srender('post.html', post=post, board=board,
                     nextpid=nextpid, prevpid=prevpid);
        
        # post = manager.post.get_post(pid)
        # if not post:
        #     raise tornado.web.HTTPError(404)
        # board = manager.board.get_board_by_id(post['bid'])
        # if post.replyid :
        #     parent = manager.post.get_post(post.replyid)
        #     root = manager.post.get_post(post.tid)
        #     firstpid = root.pid
        # else:
        #     parent = root = None
        #     firstpid = post.pid
        # children = manager.post.get_post_by_replyid(post.pid)
        # prevpid = manager.post.prev_post_pid(post.bid, post.pid)
        # nextpid = manager.post.next_post_pid(post.bid, post.pid)
        # lastpid = manager.post.get_topice_last_pid(post.tid)
        # if self.get_current_user() :
        #     userid = self.get_current_user()
        #     manager.readmark.set_read(userid, board.boardname, pid)
        # self.srender('post.html', board=board, post=post,
        #              parent=parent, root=root, children=children,
        #              firstpid=firstpid, prevpid=prevpid,
        #              nextpid=nextpid, lastpid=lastpid)

class ReplyPostHandler(BaseHandler):

    def get(self, replyid):
        reply = manager.post.get_post(replyid)
        if reply is None:
            raise tornado.web.HTTPError(404)
        if not self.get_current_user():
            raise tornado.web.HTTPError(404)
        content = fun_gen_quote(reply.owner, reply.content)
        title = reply.title if reply.title.startswith('Re:') \
            else 'Re: %s' % reply.title
        self.srender("reply.html", reply=reply, title=title,
                     content=content)

class NewPostHandler(BaseHandler):

    def get(self, boardname):
        self.render('newpost.html', boardname=boardname)

class APINewPostHandler(BaseHandler):

    def post(self):
        userid = self.get_current_user()
        if not userid:
            return self.write({
                    "success": False,
                    "content": '用户未登录',
                    })
        title=self.get_argument('title', None)
        if not title :
            return self.write({
                    "success": False,
                    "content": "标题不能为空！",
                    })
        boardname = self.get_argument('boardname', None)
        print '***', boardname
        res = boardname and boardname.isalpha() and \
            manager.board.name_and_id(boardname)
        if not res :
            return self.write({
                    "success": False,
                    "content": "错误的讨论区！",
                    })
        bid = res.bid
        boardname = res.boardname
        signnum = self.get_argument('signnum', None)
        if signnum is None or signnum < manager.usersign.get_sign_num(userid):
            signature = ''
        else:
            signature = manager.usersign.get_sign(userid, signnum)
        pid = manager.post.add_post(
            bid=bid, owner=userid, title=title,
            content=self.get_argument('content', ''), replyid=0,
            fromaddr=self.request.remote_ip,
            replyable=(self.get_argument('replyable')=='on'),
            signature=signature)
        manager.post.update_post(pid, tid=pid)
        manager.readmark.set_read(userid, boardname, pid)
        self.write({
                "success": True,
                "content": "发文成功！",
                "pid": pid,
                })

class APIReplyPostHandler(BaseHandler):

    def post(self, replyid):
        userid = self.get_current_user()
        if not userid :
            self.write({
                    'success': False,
                    'content': '用户未验证',
                    })
            return
        post = manager.post.get_post(replyid)
        boardname = manager.board.id2name(post.bid)
        signnum = self.get_argument('signnum', None)
        if signnum is None or signnum < manager.usersign.get_sign_num(userid):
            signature = ''
        else:
            signature = manager.usersign.get_sign(userid, signnum)
        pid = manager.post.add_post(
            owner=userid, title=self.get_argument('title'),
            bid=post.bid, content=self.get_argument('content'),
            replyid=replyid, fromaddr=self.request.remote_ip,
            tid=post.tid, replyable=(self.get_argument('replyable')=='on'),
            signature=signature)
        manager.readmark.set_read(userid, boardname, pid)
        self.write({
                'success': True,
                'content': '回复成功！',
                });
