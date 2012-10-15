#!/usr/bin/python2
# -*- coding: utf-8 -*-

import random
from chaofeng import PluginHolder
from chaofeng.g import mark
from chaofeng.ui import TextEditor, TextEditorAreaMixIn
import chaofeng.ascii as ac
from libframe import BaseAuthedFrame, gen_quote
from model import manager
import config
import functools

class RNEditor(TextEditor, TextEditorAreaMixIn):

    ESCAPE_LINE = '\n'

    fground_string = dict((str(x), (u'[%%3%s#]' % x, u'[#%]')) for x in range(0,8))
    bground_string = dict((str(x), (u'[%%4%s#]' % x, u'[#%]')) for x in range(0,8))
    special_style = {
        u'i':(u'[%3#]', u'[#%]'),
        u'u':(u'[%4#]', u'[#%]'),
        u'b':(u'[%1#]', u'[#%]'),
        u'l':(u'[%5#]', u'[#%]'),
        u'n':(u'[%7#]', u'[#%]'),
        }

    def _insert_style(self):
        self.hint(u'b) 背景色 f)字体色 r)样式复原')
        char = self.frame.read_secret()
        if char == 'b' :
            self.hint(u'背景颜色? 0)黑 1)红 2)绿 3)黄 4)深蓝 5)粉红 6)浅蓝 7)白')
            char2 = self.frame.read_secret()
            if char2 in self.bground_string :
                return self.bground_string[char2]
        elif char == 'f' :
            self.hint(u'字体颜色? 0)黑 1)红 2)绿 3)黄 4)深蓝 5)粉红 6)浅蓝 7)白')
            char2 = self.frame.read_secret()
            if char2 in self.fground_string :
                return self.fground_string[char2]
        elif char == 'e' :
            self.hint(u'特殊样式? i)斜体 u)下划线 b)加粗 l)闪烁 n)反转')
            char2 = self.frame.read_secret()
            if char2 in self.special_style:
                return self.special_style[char2]
        elif char == 'r' :
            return (u'[#%]', u'')
        elif char == ac.esc :
            return self.esc

    def insert_style(self):
        res = self._insert_style()
        if isinstance(res, tuple) :
            self.insert_string(*res)
        elif res is not None :
            self.force_insert_char(res)

    def insert_style_area(self):
        res = self._insert_style()
        if isinstance(res, tuple) :
            self.insert_string_area(*res)
                
    def bottom_bar(self,msg=u''):
        self.frame.push(ac.move2(24,1))
        self.frame.render(u'bottom_edit', message=msg,
                          l=self._hover_col, r=self._hover_row)
        self.fix_cursor()

    def do_command(self, cmd):
        if cmd :
            getattr(self, cmd)()
            self.bottom_bar()

    def fetch_all(self):
        text = super(RNEditor, self).fetch_all()
        return text.replace(self.esc, ac.esc)

class Editor(RNEditor):

    ESCAPE_LINE = '\n'

class BaseEditFrame(BaseAuthedFrame):

    plugin = PluginHolder([
            'after_publish_new_post',
            ])

    shortcuts = {}
    shortcuts_ui = config.shortcuts['edit_ui']
    shortcuts_2nd_start = ac.k_ctrl_u
    shortcuts_ui_2nd = config.shortcuts['edit_ui_2nd']

    def setup(self, text, spoint=0):
        assert isinstance(text, unicode)
        self._editor = self.load(Editor, text, spoint)
        self.restore_screen()

    def _init_screen(self):
        self._editor.restore_screen()

    def get(self, char):
        if char in self.shortcuts:
            self.do_command(self.shortcuts[char])
        elif char in self.shortcuts_ui :
            self._editor.do_command(self.shortcuts_ui[char])
        elif char == self.shortcuts_2nd_start :
            char = self.read_secret()
            if char in self.shortcuts_ui_2nd:
                self._editor.do_command(self.shortcuts_ui_2nd[char])
        elif ac.is_safe_char(char):
            self._editor.insert_char(char)
            self._editor.bottom_bar()

    def restore_screen(self):
        self._editor.restore_screen()
        self._editor.bottom_bar()

    def show_help(self):
        self.suspend('help', pagename='edit')
    
    def restore(self):
        self.restore_screen()

@mark('new_post')
class NewPostFrame(BaseEditFrame):

    shortcuts = {
        ac.k_ctrl_w:"finish",
        ac.k_ctrl_x:"publish",
        ac.k_ctrl_q:"show_help",
        }

    shortcuts_ui = config.shortcuts['edit_ui']

    def update_attr(self, attrs):
        self.render('edit_head', **attrs)

    READ_ATTR_PROMPT = u"[25;1H[K[1;32m0[m~[1;32m%s[m/[1;32mx[m "\
        u"选择/随机签名档 [1;32mt[m标题，[1;32mu[m回复，[1;32mq[m放弃:"

    def read_attrs(self, sign_num, boardname, replyable ):
        attrs = {
            "boardname":boardname,
            "replyable":replyable,
            "usesign":0,
            "title":u"[正在设定主題]",
            }
        if sign_num :
            attrs['usesign'] = random.randint(1, sign_num)
        self.update_attr(attrs)
        attrs['title'] = self.safe_readline(prompt=u'请输入标题：', buf_size=40)
        if not attrs['title'] :
            return
        self.update_attr(attrs)
        prompt = self.READ_ATTR_PROMPT % sign_num
        while True:
            op = self.safe_readline(buf_size=4, prompt=prompt)
            if op == '':
                break
            elif op is False or op=='q':
                return
            elif op == 't' :
                attrs['title'] = self.safe_readline(
                    prompt=u'\r\x1b[K请输入标题：',
                    buf_size=40, #prefix=attrs['title'],
                    )
                if not attrs['title'] :
                    return
            elif op == 'u' :
                attrs['replyable'] = not attrs['replyable']
            elif op == 'x' and sign_num:
                attrs['usesign'] = random.randint(1, sign_num)
            elif op.isdigit() :
                n = int(op)
                if n <= sign_num :
                    attrs['usesign'] = n
            self.update_attr(attrs)
        return attrs

    def initialize(self, boardname):
        perm = manager.query.get_board_ability(self.userid,
                                               boardname)
        if not perm[0]:
            self.goto_back()
        manager.status.set_status(self.seid,
                                  manager.status.POSTING)
        self.cls()
        attrs = self.read_attrs(manager.usersign.get_sign_num(self.userid),
                                boardname, True)
        if attrs :
            attrs['signtext'] = manager.usersign.get_sign(
                self.userid, attrs['usesign']-1) \
                if attrs['usesign'] else ''
            self._attrs = attrs
            self.setup(u'')
        else:
            self.pause_back(u'放弃发表新文章')

    def finish(self):
        self.cls()
        self.push(u'文章处理：\r\n')
        self.push(u'l) 发表文章 r)寄回信箱 t)修改标题 a)取消发文 e)再编辑？: ')
        char = self.readchar(acceptable=lambda x:x in 'lrtae',
                             cancel='a', default=u'l')
        if char == 'l':
            self.publish_and_goto_back(self._attrs, self._editor.fetch_all())
        if char == 'r':
            self.backup(self._editor.fetch_all())
        if char == 't':
            self.modify_title()
        if char == 'a':
            self.goto_back()
        self.restore_screen()

    def publish(self):
        self.publish_and_goto_back(self._attrs, self._editor.fetch_all())

    def publish_and_goto_back(self, attrs, text):
        pid = manager.action.new_post(attrs['boardname'],
                                      self.userid,
                                      attrs['title'],
                                      text,
                                      self.session.ip,
                                      config.BBS_HOST_FULLNAME,
                                      replyable=attrs['replyable'],
                                      signature=attrs['signtext'])
        self.session['lastpid'] = pid
        for func in self.plugin.get_all_hook('after_publish_new_post'):
            func(self, pid, attrs, text)
        self.goto_back()

    def backup(self, text):
        manager.action.send_mail('archive_', self.userid,
                                 content=text)
        self.restore_screen()

    def modify_title(self):
        self.push(u'\r\n开始编辑标题，[32m^C[m取消\r\n')
        self.push(u'现在的标题：%s\r\n' % self._attrs['title'])
        self.push(u'修改为：')        
        title = self.readline()
        if title :
            self._attrs['title'] = title
            self.push(u'\r\n修改成功！')
            self.pause()
        self.restore_screen()

@mark('_reply_post_o')
class ReplyPostFrame(BaseEditFrame):

    shortcuts = {
        ac.k_ctrl_w : "finish",
        ac.k_ctrl_x: "publish",
        ac.k_ctrl_q:"show_help",
        }

    READ_ATTR_PROMPT = u"[25;1H[K[1;32m0[m~[1;32m%s[m/[1;32mx[m "\
        u"选择/随机签名档 [1;32mt[m标题，[1;32mu[m回复，[1;32mq[m放弃:"

    def update_attr(self, attrs):
        self.render('edit_head', **attrs)

    def read_attrs(self, sign_num, boardname, replyable, title):
        attrs = {
            "boardname":boardname,
            "replyable":replyable,
            "usesign":0,
            "title":title,
            }
        if sign_num :
            attrs['usesign'] = random.randint(1, sign_num)
        self.update_attr(attrs)
        prompt = self.READ_ATTR_PROMPT % sign_num
        while True:
            op = self.safe_readline(buf_size=4, prompt=prompt)
            if op == '':
                break
            elif op is False or op=='q':
                return None
            elif op == 't' :
                attrs['title'] = self.safe_readline(prompt=u'\r\x1b[K请输入标题：',
                                                    prefix=attrs['title'],buf_size=40)
                if not attrs['title'] :
                    return
            elif op == 'u' :
                attrs['replyable'] = not attrs['replyable']
            elif op == 'x' and sign_num:
                attrs['usesign'] = random.randint(1, sign_num)
            elif op.isdigit() :
                n = int(op)
                if n <= sign_num :
                    attrs['usesign'] = n
            self.update_attr(attrs)
        return attrs

    def initialize(self, boardname, post):
        perm = manager.query.get_board_ability(self.userid, boardname)
        if not perm[0] :
            self.goto_back()
        post = manager.post.get_post(post['pid'])  ## reload to get date in realtime
        if not (perm[1] and post['replyable']):
            self.pause(u'你没有发文权力或本文禁止回复！')
        manager.status.set_status(self.seid,
                                  manager.status.POSTING)
        self.cls()
        title = post['title'] if post['title'].startswith('Re:')\
            else u'Re: %s' % post['title']
        attrs = self.read_attrs(manager.usersign.get_sign_num(self.userid),
                                boardname, True, title)
        if not attrs:
            self.goto_back()
        attrs['signtext'] = manager.usersign.get_sign(
            self.userid, attrs['usesign'] -1) if attrs['usesign'] else ''
        attrs['replyid'] = post['pid']
        self._attrs = attrs
        text = gen_quote(post)
        self.setup(text=text)

    def finish(self):
        self.cls()
        self.push(u'文章处理：\r\n')
        self.push(u'l) 发表文章 r)寄回信箱 t)修改标题 a)取消发文 e)再编辑？: ')
        char = self.readchar(acceptable=lambda x:x in 'lrtae',
                             cancel='a', default=u'l')
        if char == 'l':
            self.publish_and_goto_back(self._attrs, self._editor.fetch_all())
        if char == 'r':
            self.backup(self._editor.fetch_all())
        if char == 't':
            self.modify_title()
        if char == 'a':
            self.goto_back()
        self.restore_screen()

    def publish(self):
        self.publish_and_goto_back(self._attrs, self._editor.fetch_all())

    def publish_and_goto_back(self, attrs, text):
        pid = manager.action.reply_post(attrs['boardname'],
                                        self.userid,
                                        attrs['title'],
                                        text,
                                        self.session.ip,
                                        config.BBS_HOST_FULLNAME,
                                        attrs['replyid'],
                                        replyable=attrs['replyable'],
                                        signature=attrs['signtext'])
        for func in self.plugin.get_all_hook('after_publish_new_post'):
            func(self, pid, attrs, text)
        self.goto('board', boardname=attrs['boardname'], pid=pid)

    def modify_title(self):
        self.push(u'\r\n开始编辑标题，[32m^C[m取消\r\n')
        self.push(u'现在的标题：%s\r\n' % self._attrs['title'])
        self.push(u'修改为：')        
        title = self.readline()
        if title :
            self._attrs['title'] = title
            self.push(u'\r\n修改成功！')
            self.pause()
        self.restore_screen()

    def backup(self, text):
        manager.action.send_mail('archive_', self.userid,
                                 content=text)
        self.restore_screen()

@mark('_edit_post_o')
class EditPostFrame(BaseEditFrame):

    shortcuts = {
        ac.k_ctrl_w:"finish",
        ac.k_ctrl_x:"publish",
        ac.k_ctrl_q:"show_help",
        }
    shortcuts_ui = config.shortcuts['edit_ui']

    def initialize(self, board, post):
        manager.status.set_status(self.seid,
                                  manager.status.EDIT)
        self.cls()
        self.boardname = board['boardname']
        self.pid = post['pid']
        self.setup(text=post['content'])

    def finish(self):
        self.cls()
        self.push(u'修改文章：\r\n')
        self.push(u'l) 确认修改 r)寄回信箱 a)取消发文 e)再编辑？： ')
        char = self.readchar(acceptable=lambda x:x in 'lrae',
                             cancel='a', default=u'l')
        if char == 'l':
            self.modify_and_goto_back(self._editor.fetch_all())
        if char == 'r':
            self.backup(self._editor.fetch_all())
        if char == 'a':
            self.goto_back()
        self.restore_screen()

    def modify_and_goto_back(self, text):
        manager.action.update_post(self.userid, self.pid, text)
        self.goto_back()

    def publish(self):
        self.modify_and_goto_back(self._editor.fetch_all())

    def backup(self, text):
        manager.action.send_mail('archive_', self.userid,
                                 content=text)
        self.restore_screen()

@mark('edit_text')
class EditFileFrame(BaseEditFrame):

    shortcuts = {
        ac.k_ctrl_w:"finish",
        ac.k_ctrl_x:"publish",
        ac.k_ctrl_q:"show_help",
        }
    shortcuts_ui = config.shortcuts['edit_ui']

    def initialize(self, filename, text=u'', l=0):
        self.cls()
        self._filename = filename
        if text is None:
            text = u'';
        self.setup(text=text, spoint=l)

    def setup(self, text, spoint):
        assert isinstance(text, unicode) or isinstance(text, list)
        self._editor = self.load(Editor, text, spoint)
        self.restore_screen()

    def finish(self):
        self.cls()
        self.push(u'修改文章：\r\n')
        self.push(u'l) 确认修改 r)寄回信箱 a)取消发文 e)再编辑？： ')
        char = self.readchar(acceptable=lambda x:x in 'lrae',
                             cancel='a', default=u'l')
        if char == 'l':
            self.modify_and_goto_back(self._editor.fetch_all())
        if char == 'r':
            self.backup(self._editor.fetch_all())
        if char == 'a':
            self.goto_back()
        self.restore_screen()

    def publish(self):
        self.modify_and_goto_back(self._editor.fetch_all())

    def modify_and_goto_back(self, text):
        self.session['__edit__'] = (self._filename, text)
        self.goto_back()

    def backup(self, text):
        manager.action.send_mail('archive_', self.userid,
                                 content=text)
        self.restore_screen()

@mark('_repost_post_o')
class RepostPostFrame(BaseAuthedFrame):

    def initialize(self, boardname, post):
        self.cls()
        self.render('repost_notice')
        where = self.safe_readline(prompt=u'要转贴到：')
        board = manager.board.get_board(where)
        perm = manager.query.get_board_ability(self.userid,
                                               board['boardname'])
        if board and perm[1]:
            where = board['boardname']
            if self.confirm(u'\r\n转载 `%s` 到 %s 版？[y/n]：' % \
                                (post['title'] ,where) , default='n') :
                text = self.render_str('repost-t', boardname=boardname, **post)
                manager.action.new_post(board['boardname'],
                                        self.userid,
                                        post['title'],
                                        text,
                                        self.session.ip,
                                        config.BBS_HOST_FULLNAME,
                                        replyable=post['replyable'],
                                        signature='')
                self.pause_back(u'\r\n转载成功！')
            else:
                self.pause_back(u'\r\n取消操作')
        else:
            self.pause_back(u'\r\n无该讨论区！')

@mark('edit_text_rn')
class RNEditFileFrame(EditFileFrame):

    def setup(self, text, spoint):
        assert isinstance(text, unicode)
        self._editor = self.load(RNEditor, text, spoint)
        self.restore_screen()

def handler_edit(f):
    '''Wrapper for restore method.'''
    @functools.wraps(f)
    def wrapper(self):
        if self.session['__edit__']:
            filename, text = self.session.pop('__edit__')
            getattr(self, 'handler_%s' % filename)(text)
        return f(self)
    return wrapper
