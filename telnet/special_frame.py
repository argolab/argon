# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from argo_frame import ArgoFrame
from chaofeng import EndInterrupt
from chaofeng.g import mark
import chaofeng.ascii as ac
from model import manager
from view import ArgoTextBoxFrame

@mark('bad_ending')
class BadEndingFrame(ArgoFrame):

    def bad_ending(self,e):
        try:
            manager.auth.safe_logout(self.userid,self.seid)
        except AttributeError:
            pass            
        self.write(ac.clear + u'崩溃啦~ T.T 麻烦请报告管理员~\r\n'+ac.reset)
        self.pause()
        self.close()

@mark('history')
class ArgoHistoryFrame(ArgoTextBoxFrame):

    @property
    def status(self):
        return dict()

    @classmethod
    def describe(self,s):
        return u'浏览历史记录'

    def initialize(self):
        super(ArgoHistoryFrame,self).initialize()
        self.show_history()

    def show_history(self):
        items = map(lambda x : self.getdesc(x),self.history)
        self.set_text(self.render_str('history',items=items))

    def finish(self,args):
        self.goto_back_nh()

    def show_help(self):
        self.suspend('help',page='history')
    
@mark('finish')
class Finish(ArgoFrame):

    def initialize(self):
        self.finish(None)
        self.render('undone')
        self.pause()
        self.close()

    def finish(self,e):
        try:
            manager.auth.safe_logout(self.userid,self.seid)
        except AttributeError:
            pass            

    def bad_ending(self,e):
        self.finish(e)
        self.write(ac.clear + u'崩溃啦~ T.T 麻烦请报告管理员~\r\n'+ac.reset)
        self.pause()
        self.close()
