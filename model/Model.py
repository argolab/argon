#!/usr/bin/python2
# -*- coding: utf-8 -*-

from globaldb import global_conn,global_cache
from MySQLdb import ProgrammingError
import bcrypt,time
from datetime import datetime
import random
# import perm
import logging
import status
import traceback
from error import *

logger = logging.getLogger('model')

class Manager(object):

    def __init__(self, db, ch, modulescls, name=None):
        u'''
        Init the manager object. Simplely setup the database
        connection and redis connection. And then, load the
        modulescls use the name[classname] as bindname, or
        use the lower of classname if name[classname] is None.
        
        `modulescls` should be a list of Model Class. 

        DB is an object that has following methods(like tornado.database):

          db.query(sql, *para)
          db.get(sql, *para)
          db.execute(sql, *para)
          db.executemany(sql, paras)
          db.execute_paragraph(sql)

        CH is an object that like stand redis.ch .
          
        '''
        self.db = db
        self.ch = ch
        for modclass in modulescls:
            module = modclass(self)
            modname = (name and name.get(modclass.__name__))\
                or modclass.__name__.lower()
            self.bind(modname, module)
        
    def bind(self, bindname, module):
        u'''Bind the module into the manager use the bindname.
        So we can use manager.bindname to use the module.
        '''
        setattr(self, bindname, module)

    def get_module(self, bindname):
        u'''Get the module the bindname. Raise ValueError if
        no such model with the bindname.'''
        try:
            return getattr(self, bindname)
        except AttributeError:
            raise ValueError(u'No such model with the bindname')
             
class MetaModel(type):

    '''
    A meta class that give the magic to record all submodel,
    and some special action.
    '''

    all_model = []  ## use to record all model

    def __new__(cls,names,bases,attrs):
        '''
        Call the classmethod `__clsinit__` if defined, and
        simplely append the new model into all_model.
        '''
        old_cls = cls
        cls = super(MetaModel,cls).__new__(cls,names,bases,attrs)
        if attrs.get('__clsinit__') is not None:
            cls.__clsinit__(names,bases,attrs,old_cls)
        cls.__modelname__ = names
        old_cls.all_model.append(cls)
        return cls

class Model(object):
    
    u'''
    A base class for a model. It implemented some common methods as well.
    Basic useage read the Manage class.
    '''

    __metaclass__ = MetaModel

    def __init__(self, manager):
        u'''

        NEVER CALL INIT A NEW MODEL EXCEPT THAT YOU KNOW WHAT YOU DO
        USE THE MANAGER

        Load this model into manager, use __class__.__name__.lower()
        as bindname if bindname is not set.
        
        An model fix other model, may rewrite this metheds to set some
        alise for other model, i.e.:
        
           def __init__(self, manager):
               super(NewModel, self).__init__(manager)
               self.model_1 = manager.model_1
               self.model_2 = manager.model_2
               
        '''
        self.db = manager.db  # Alias self.db as manager.db
        self.ch = manager.ch

    def table_select_all(self,tablename):
        return self.db.query("SELECT * FROM `%s`" % tablename)

    def table_get_by_key(self,tablename,key,value):
        return self.db.get("SELECT * FROM `%s` WHERE %s = %%s" %\
                               (tablename,key),
                           value)

    def execute_paragraph(self, para):
        self.db.execute_paragraph(para)

    def table_insert(self,tablename,attr):
        names,values = zip(*attr.items())
        cols = ','.join(map(str,names))
        vals = ','.join(('%s',) * len(values))
        return self.db.execute("INSERT INTO `%s` (%s) VALUES (%s)" % \
                                   (tablename, cols,vals),
                               *values)
    
    def table_update_by_key(self,tablename,key,value,attr):
        names,values = zip(*attr.items())
        set_sql = ','.join( map(lambda x: "%s = %%s" % x,names))
        return self.db.execute("UPDATE `%s` SET %s WHERE %s = %%s" % \
                                   (tablename, set_sql, key),
                               *(values + (value,)))

    def table_delete_by_key(self,tablename,key,value):
        return self.db.execute("DELETE FROM `%s` WHERE %s = %%s" % \
                                   (tablename, key),
                               value)

    def table_select_by_key(self,tablename,what,key,value):
        return self.db.get("SELECT %s FROM `%s` WHERE %s = %%s" %\
                               (what, tablename, key),
                           value)

    def table_get_listattr(self, tablename, what, key, value):
        res = self.db.get("SELECT %s FROM `%s` WHERE %s=%%s"%(what, tablename, key),
                          value)
        return res and ( (res[what] and res[what].split(':')) or [])

    def table_update_listattr(self, tablename, what, listattr, key, value):
        r = ':'.join(listattr)
        return self.db.execute("UPDATE `%s` SET %s=%%s WHERE %s=%%s" % \
                                   (tablename, what, key),
                               r, value)

class Section(Model):

    u'''
    Section stands the classification of a board.
    
    db: argo_sectionhead
    '''

    table = 'argo_sectionhead'  ## The MySQL table name

    def get_all_section(self):
        u'''Return all sections'''
        return self.table_select_all(self.table)

    def get_all_section_with_rownum(self):
        u'''Return all sections with rownum.'''
        d = self.get_all_section()
        return with_index(d, 0)

    def get_section(self,name):
        u''' Get a section by sectionname.'''
        return self.table_get_by_key(self.table, 'sectionname', name)

    def get_section_by_sid(self, sid):
        u'''Get a section by sid'''
        return self.table_get_by_key(self.table, 'sid', sid)

    def add_section(self,**kwargs):
        u'''Add a section. kwargs is the key/value the section will
        has. It may by `sid`, `sectionaname`, `description`,
        or `introduction`. '''
        return self.table_insert(self.table, kwargs)
    
    def update_section(self, sid, **kwargs):
        u'''Update a secion's attr by sid. The attr is same as in
        add_section. '''
        return self.table_update_by_key(self.table, 'sid', sid, kwargs)
    
    def del_section(self,sid):
        u'''Delete a section by sid.'''
        return self.table_delete_by_key(self.table, 'sid', sid)
    
    def name2id(self,sectionname):
        u'''Covert the sectioname to sid, return None if no such
        sectionname. '''
        d = self.table_select_by_key(self.table, 'sid', 'sectionname',
                                     sectionname)
        return d and d['sid']

    def id2name(self,sid):
        u'''Covert the sid to sectioname, return None if no such
        sid. '''
        n = self.table_select_by_key(self.table, 'sectionname', 'sid', sid)
        return n and n['sectionname']

    def get_max_sid(self):
        u'''Return the max sid.'''
        n = self.db.get("SELECT max(sid) FROM %s" % self.table)
        return n or 0
        
class Board(Model):

    u'''
    The low level operation of boards. It just wrap up some opearator
    with SQL database.
    The recommend board was implemented here.

    db:argo_boardhead
       argo_recommend
    '''

    __ = 'argo_boardhead'
    _r = 'argo_recommend'
    
    def get_by_sid(self,sid):
        return self.db.query("SELECT * FROM `%s` WHERE sid = %%s" % self.__,
                             sid)

    def get_all_boards(self):
        return self.table_select_all(self.__)

    def get_board(self,name):
        return self.table_get_by_key(self.__, 'boardname', name)

    def get_recommend(self):
        return self.db.query(
            "SELECT %s.* FROM `%s` INNER JOIN %s ON "
            "%s.bid = %s.bid ORDER BY %s.bid" % \
                (self.__, self.__, self._r, self.__, self._r, self.__))

    def add_recommend(self,bid):
        return self.table_insert(self._r,  dict(bid=bid))

    def del_recommend(self,bid):
        return self.table_delete_by_key(self._r, 'bid', bid)

    def get_board_by_id(self,bid):
        return self.table_get_by_key(self.__, 'bid', bid)

    def add_board(self,**kwargs):
        return self.table_insert(self.__, kwargs)
    
    def update_board(self,bid,**attr):
        return self.table_update_by_key(self.__, 'bid', bid, attr)
    
    def del_board(self,bid):
        return self.table_delete_by_key(self.__, 'bid', bid)
    
    def name2id(self,boardname):
        logger.debug('name2id -- %s',boardname)
        d = self.table_select_by_key(self.__, 'bid', 'boardname', boardname)
        return d and d['bid']
    
    def id2name(self,bid):
        d = self.table_select_by_key(self.__, 'boardname', 'bid', bid)
        return d and d['boardname']

    def name_and_id(self, boardname):
        return self.db.get("SELECT boardname, bid "
                             "FROM %s WHERE boardname=%%s" % self.__,
                             boardname)

    def update_attr_plus1(self,bid,key):
        return self.db.execute("UPDATE %s SET %s = %s +1 WHERE bid = %%s" % \
                                   (self.__, key, key),
                               bid)

    def get_board_bm(self, boardname):
        return self.table_get_listattr(self.__,  'bm', 'boardname', boardname)

    def set_board_bm(self, boardname, bms):
        return self.table_update_listattr(self.__, 'bm', bms, 'boardname', boardname)

class Favourite(Model):

    u'''
    low level operation of user favourite.

    ch:
        {set} argo:favourite:$userid
    '''

    keyf = "argo:favourite:%s"
    default_userid = '+default+'

    def init_user_favourite(self, userid):
        key = self.keyf % userid
        self.ch.delete(key)
        self.ch.sunionstore(key, self.keyf % self.default_userid)

    def add(self, userid, bid):
        u''' Add an board into user's favourtie.'''
        key = self.keyf % userid
        self.ch.sadd(key, bid)
                      
    def remove(self, userid, bid):
        key = self.keyf % userid
        self.ch.srem(key, bid)

    def get_all(self, userid):
        u'''Return a set holds all board's name in user's favourite.'''
        key = self.keyf % userid
        return self.ch.smembers(key)

    def is_fav(self, userid, bid):
        key = self.keyf % userid
        return self.ch.sismember(key, bid)

    def add_default(self, bid):
        self.add(self.default_userid, bid)

    def remove_default(self, bid):
        self.remove(self.default_userid, bid)

class Post(Model):

    u'''
    Low level operation of post.

    db: argo_filehead;
    ch: [hash] : argo_lastpost[boardname]

    '''

    _index_table = 'argo_filehead'
    _junk_table= 'argo_filehead_junk'

    FILTER_G = 'gmark=1'
    FILTER_M = 'mmark=1'
    FILTER_O = 'replyid=0'

    def sql_filter_tid(self, tid):
        return 'tid=%s' % tid

    def sql_filter_owner(self, owner):
        return 'owner=%s' % owner
    

    def _move_post(self, tablename, pid, new_tablename):
        self.db.execute("INSERT INTO `%s` "
                        "(SELECT * "
                        "FROM `%s` "
                        "WHERE pid=%%s)" % (new_tablename, tablename), pid)

        return self.db.execute("DELETE FROM %s "
                               "WHERE pid=%%s" % tablename, pid)

    def _move_post_range(self, tablename, new_tablename, bid, start, end):
        self.db.execute("INSERT INTO `%s` "
                        "(SELECT * "
                        "FROM `%s` "
                        "WHERE bid=%%s AND pid>=%%s AND "
                        "pid<%%s AND not flag)" % \
                            (new_tablename, tablename),
                        bid, start, end)
        return self.db.execute("DELETE FROM %s "
                               "WHERE bid=%%s AND pid>=%%s AND pid<%%s "
                               "AND not flag" % tablename, bid, start, end)

    def _move_post_many(self, tablename, new_tablename, bid, pids):
        self.db.executemany("INSERT INTO `%s` "
                            "(SELECT * "
                            "FROM `%s` "
                            "WHERE bid=%s AND pid=%%s AND not flag)" % \
                                (new_tablename, tablename, bid),
                            pids)
        return self.db.executemany("DELETE FROM %s "
                                   "WHERE bid=%s AND pid=%%s AND not flag" %\
                                       (tablename, bid),
                                   pids)

    def remove_post_junk(self, pid):
        return self._move_post(self._index_table, pid, self._junk_table)

    def remove_post_junk_range(self, bid, start, end):
        return self._move_post_range(self._index_table, self._junk_table,
                                     bid, start, end)

    def remove_post_personal(self, pid):
        return self.db.execute("DELETE FROM %s WHERE pid=%%s" % \
                                   self._index_table,
                               pid)

    def get_junk_posts(self, bid, num, limit):
        return self.db.query("SELECT * FROM `%s` WHERE bid=%%s ORDER BY pid "
                             "LIMIT %%s,%%s" % self._junk_table,
                             bid, num, limit)

    def get_rank_num(self, bid, pid):
        res = self.db.get('SELECT count(*) as sum '
                          'FROM `%s` '
                          'WHERE bid=%%s '
                          'AND pid<%%s '
                          'ORDER BY pid' % self._index_table, bid,
                          pid)
        return res and res['sum']

    def get_rank_num_cond(self, bid, pid, cond):
        res = self.db.get('SELECT count(*) as sum '
                          'FROM `%s` '
                          'WHERE bid=%%s AND pid<%%s AND %%s '
                          'ORDER BY pid' % (self._index_table, bid, cond),
                          pid)
        return res and res['sum']

    def rank2pid(self, bid, rank):
        res = self.db.get("SELECT pid FROM `%s` "
                          "WHERE bid=%%s ORDER BY pid "
                          "LIMIT %%s, 1" % self._index_table,
                          bid, rank)
        return res and res['pid']

    def get_post_total(self, bid):
        res = self.db.get("SELECT count(pid) as total "
                          "FROM %s WHERE bid=%%s" % self._index_table, bid)
        return res and res['total']

    #####################

    def get_posts(self, bid, num, limit):
        sql = "SELECT * FROM `%s` WHERE bid = %%s ORDER BY pid LIMIT %%s,%%s"
        res = self.db.query( sql % self._index_table, bid, num, limit)
        return with_index(res, num)

    def get_posts_loader(self, bid, cond=''):
        if cond :
            sql = "SELECT * FROM `%s` WHERE %s AND bid = %s ORDER BY pid LIMIT %%s,%%s" % \
                (self._index_table, bid, cond)
        else:
            sql = "SELECT * FROM `%s` WHERE bid = %s ORDER BY pid LIMIT %%s,%%s" % \
                (self._index_table, bid)
        return lambda start, limit: with_index(
            self.db.query(sql, start, limit), start,)

    def get_posts_counter(self, bid , cond=''):
        if cond :
            sql = "SELECT count(*) as sum FROM `%s` WHERE %s AND bid = %s" % \
                (self._index_table, cond, bid)
        else:
            sql = "SELECT count(*) as sum FROM `%s` WHERE bid = %s" %\
            (self._index_table, bid)
        return lambda : self.db.get(sql)['sum']

    def get_posts_total(self, bid):
        return self.db.get("SELECT count(*) as sum FROM %s WHERE bid = %%s" %\
                self._index_table, bid)['sum']

    def get_posts_g(self, bid, num, limit):
        res = self.db.query("SELECT * FROM `%s` WHERE bid = %%s AND mark_g = 1 ORDER BY pid LIMIT %%s,%%s" %\
                                self._index_table, bid, num, limit)
        return with_index(res, num)

    def get_posts_g_total(self, bid):
        return self.db.get("SELECT count(*) as sum FROM `%s` WHERE bid = %%s AND mark_g = 1" %\
                self._index_table, bid)['sum']

    def get_posts_m(self,bid,num,limit):
        res = self.db.query("SELECT * FROM `%s` WHERE bid = %%s AND mark_m = 1 ORDER BY pid LIMIT %%s,%%s" %\
                                       self._index_table, bid, num, limit)
        return with_index(res, num)

    def get_posts_m_total(self, bid):
        return self.db.get("SELECT count(*) as sum FROM `%s` WHERE bid = %%s AND mark_m = 1" %\
                self._index_table, bid)['sum']

    def get_posts_topic(self, bid, num, limit):
        res = self.db.query("SELECT * FROM `%s` WHERE bid = %%s AND replyid=0 ORDER BY pid LIMIT %%s,%%s" %\
                                self._index_table, bid, num, limit)
        return with_index(res, num)

    def get_posts_topic_total(self, bid):
        return self.db.get("SELECT count(*) as sum FROM %s WHERE bid = %%s AND replyid=0" %\
                self._index_table, bid)['sum']

    def get_posts_onetopic(self,tid,bid,num,limit):
        res = self.db.query("SELECT * FROM `%s` WHERE bid = %%s AND tid=%%s ORDER BY pid LIMIT %%s,%%s" %\
                                self._index_table, bid, tid, num, limit)
        return with_index(res, num)

    def get_posts_onetopic_total(self, tid, bid):
        return self.db.get("SELECT count(*) as sum FROM %s WHERE bid = %%s AND tid=%%s" %
                self._index_table, bid, tid)['sum']

    def get_posts_owner(self,author,bid,num,limit):
        res = self.db.query("SELECT * FROM `%s` WHERE bid = %%s AND owner=%%s ORDER BY pid LIMIT %%s,%%s" %\
                                self._index_table, bid, author, num, limit)
        return with_index(res, num)

    def get_posts_owner_total(self, author, bid):
        return self.db.get("SELECT count(*) as sum FROM %s WHERE bid = %%s AND owner=%%s" %
                self._index_table, bid, author)['sum']

    ####################

    def get_last_pid(self, bid):
        res = self.db.get("SELECT max(pid) as maxpid FROM `%s` WHERE bid = %%s" % \
                               self._index_table, bid)
        return res and res['maxpid']

    def get_post_loader(self, bid):
        sql_next = "SELECT * FROM `%s` WHERE bid = %s AND pid > %%s ORDER BY pid LIMIT 1" % (self._index_table, bid)
        sql_prev = "SELECT * FROM `%s` WHERE bid = %s AND pid < %%s ORDER BY pid DESC LIMIT 1" % (self._index_table,bid)
        fun = self.db.get
        return (lambda pid : fun(sql_next, pid),
                lambda pid : fun(sql_prev, pid))

    def get_cond_post_loader(self, bid, cond):
        sql_next = "SELECT * FROM `%s` WHERE bid = %s AND pid > %%s AND %s ORDER BY pid LIMIT 1" %\
                (self._index_table, bid, cond)
        sql_prev = "SELECT * FROM `%s` WHERE bid = %s AND pid < %%s AND %s ORDER BY pid DESC LIMIT 1" %\
                (self._index_table, bid, cond)
        fun = self.db.get
        return (lambda pid : fun(sql_next, pid),
                lambda pid : fun(sql_prev, pid))

    def get_topic_post_loader(self, bid, tid):
        assert isinstance(tid, long)
        sql_next = "SELECT * FROM `%s` WHERE bid = %s AND pid > %%s AND tid=%s ORDER BY pid LIMIT 1" % (self._index_table, bid, tid)
        sql_prev = "SELECT * FROM `%s` WHERE bid = %s AND pid < %%s AND tid=%s ORDER BY pid DESC LIMIT 1" % (self._index_table, bid, tid)
        fun = self.db.get
        return (lambda pid : fun(sql_next, pid),
                lambda pid : fun(sql_prev, pid))

    def get_post(self, pid):
        return self.table_get_by_key(self._index_table, 'pid', pid)

    def get_post_by_replyid(self, replyid):
        return self.db.query("SELECT pid,title FROM %s "
                             "WHERE replyid=%%s "
                             "ORDER BY pid DESC LIMIT 5" % self._index_table,
                             replyid)

    def prev_post(self, bid, pid):
        return self.db.get("SELECT * FROM `%s` WHERE bid = %%s AND pid < %%s ORDER BY pid DESC LIMIT 1" % self._index_table, bid, pid)

    def next_post(self, bid, pid):
        return self.db.get("SELECT * FROM `%s` WHERE bid = %%s AND pid > %%s ORDER BY pid LIMIT 1" %\
                               self._index_table, bid, pid)

    def prev_three_post(self, bid, pid):
        res = self.db.get("SELECT pid FROM `%s` "
                          "WHERE bid=%%s AND pid<=%%s "
                          "ORDER BY pid DESC LIMIT 3, 1" % self._index_table,
                          bid, pid)
        return res and res['pid']

    def get_posts_after_pid(self, bid, pid, limit):
        return self.db.query("SELECT * FROM `%s` "
                             "WHERE bid = %%s AND pid >= %%s LIMIT %%s" % self._index_table,
                             bid, pid, limit)

    def get_topice_last_pid(self, tid):
        res = self.db.get("SELECT pid FROM `%s` "
                          "WHERE tid=%%s "
                          "ORDER BY pid DESC LIMIT 1" % self._index_table,
                          tid)
        return res and res['pid']        

    def prev_post_pid(self, bid, pid):
        res = self.db.get("SELECT pid FROM `%s` WHERE bid = %%s AND pid < %%s ORDER BY pid DESC LIMIT 1" %\
                              self._index_table, bid, pid)
        return res and res['pid']

    def next_post_pid(self, bid,pid):
        res = self.db.get("SELECT pid FROM `%s` WHERE bid = %%s AND pid > %%s ORDER BY pid LIMIT 1" %\
                              self._index_table, bid, pid)
        return res and res['pid']

    def add_post(self,**kwargs):
        pid = self.table_insert(self._index_table, kwargs)
        return pid

    def update_post(self, pid, **kwargs):
        return self.table_update_by_key(self._index_table, 'pid', pid, kwargs)

    def del_post(self, pid):
        u'''
            Only remove users own posts.
        '''
        return self.table_delete_by_key(self._index_table, 'pid', pid)

    def pid2tid(self,pid):
        res = self.table_select_by_key(self._index_table,
                                       'tid','pid',pid)
        return res and res['tid']

    def pid2title(self, pid):
        res = self.table_select_by_key(self._index_table,
                                       'title','pid',pid)
        return res and res['title']

    def index2pid(self, bid , index):
        if index <=0 : return 0
        res = self.db.get("SELECT pid FROM `%s` WHERE bid = %%s ORDER BY pid LIMIT %%s,1" %
                self._index_table, bid, index)
        if res :
            return res['pid']
        else:
            return self.get_last_pid(bid)+1

class UserInfo(Model):

    u'''
    Low level operation of user's info.
    db: argo_user
    '''

    __ = 'argo_user'

    def get_user(self,name):
        return self.table_get_by_key(self.__, 'userid', name)

    def get_avatar(self, userid):
        res = self.db.get("SELECT iconidx FROM %s "
                          "WHERE userid=%%s" % self.__,
                          userid)
        return res and res['iconidx']

    def add_user(self,**kwargs):
        return self.table_insert(self.__, kwargs)

    def update_user(self,userid,**kwargs):
        return self.table_update_by_key(self.__, 'userid', userid, kwargs)

    def del_user(self,userid):
        u'''
        Never delete a user.
        '''
        pass

    def name2id(self,userid):
        u'''
        Check if the userid is in database. Return the uid if so,
        or None if not.
        '''
        d = self.table_select_by_key(self.__, 'uid', 'userid', userid)
        return d and d['uid']

    def select_attr(self,userid,sql_what):
        return self.db.get("SELECT %s FROM `%s` WHERE userid = %%s" % (sql_what, self.__),
                           userid)

    def safe_userid(self, userid):
        res = self.db.get("SELECT userid FROM `%s` "
                          "WHERE userid=%%s" % self.__,
                          userid)
        return res and res['userid']

class Status(Model):

    u'''
    The module include some action about online status record.

    Each connection has a unique (userid,sessionid) pair.
    
    Every login should first call the login() method to update
    amount of the online , and it will return a number as the
    sessionsid. After logout, logout() should be called to
    clear this.

    Every *session* has a status to holds the online status,
    set_status , get_status, clear_status are about this.
    
    When it's enter/exit a board, enter_board/exit_board should
    be called.

    ch :

       {string} argo:status_count :: next_sessionid

       {hash} argo:status_ip[sessionid] | primary ==> session's remote ip

       {hash} argo:status_userid[sessionid] ==> userid
       {hash} argo:status_status[sessionid] ==> status 

       {hash} argo:status_boardonline[boardname] ==> total_num in board

       {set} argo:status_user_session[userid] ==> user's sessionid

       {order map }
          argo:status_map[rank_score] ==> session id
    '''

    for k in status.status_display:
        locals()[k] = k

    max_login = 9999

    _count = 'argo:status_count'
    _ip = 'argo:status_ip'
    _status = 'argo:status_status'
    _userid = 'argo:status_userid'
    _boardonline = 'argo:status_boardonline'
    _user_session = 'argo:status_user_session:%s'
    _map = 'argo:status_map'
    
    def new_session(self, remote, userid, status, rank_score):
        sessionid = self.ch.incr(self._count)
        self.ch.hset(self._ip, sessionid, remote)
        self.ch.hset(self._status, sessionid, status)
        self.ch.hset(self._userid, sessionid, userid)
        self.ch.sadd(self._user_session % userid, sessionid)
        self.ch.zadd(self._map, sessionid, rank_score)
        return sessionid

    def logout(self, sessionid):
        self.ch.hdel(self._status, sessionid)
        userid = self.ch.hget(self._userid, sessionid)
        self.ch.hdel(self._userid, sessionid)
        self.ch.srem(self._user_session % userid, sessionid)
        self.ch.zrem(self._map, sessionid)
        self.ch.hdel(self._ip, sessionid)

    def set_status(self, sessionid, status):
        return self.ch.hset(self._status, sessionid, status)

    def get_status(self, sessionid):
        return self.ch.hget(self._status, sessionid)

    def total_online(self):
        return self.ch.hlen(self._ip)

    def enter_board(self, boardname):
        self.ch.hincrby(self._boardonline, boardname)

    def exit_board(self, boardname):
        self.ch.hincrby(self._boardonline, boardname, -1)

    def board_online(self, boardname):
        return self.ch.hget(self._boardonline, boardname) or 0

    def get_rank(self, sessionid):
        return self.ch.zrank(self._map, sessionid)

    def get_session(self, sessionid):
        return dict(
            sessionid=sessionid,
            userid=self.ch.hget(self._userid, sessionid),
            status=self.ch.hget(self._status, sessionid),
            ip=self.ch.hget(self._ip, sessionid)
            )

    def get_sessionid_rank(self, start, limit):
        return self.ch.zrange(self._map, start, start+limit)

    def get_session_rank(self, start, limit):
        return map(self.get_session, self.get_sessionid_rank(start, limit))

    def clear_all(self):
        all_sesions = self.ch.hkeys(self._ip)
        for s in all_sesions:
            self.logout(s)
        self.ch.delete(self._boardonline)

class Mail(Model):

    u'''
    low level operation of mail.
    db: argo_mailhead

    '''

    FLAG_M_MARK = 1

    _index_table = 'argo_mailhead'

    def send_mail(self, **kwargs):
        return self.table_insert(self._index_table, kwargs)

    def set_m_mark(self, mail):
        mail['mark_m'] = not mail['mark_m']
        self.db.execute("UPDATE `%s` SET mark_m=%s WHERE mid=%%s" % self._index_table,
                        mail['mark_m'], mail['mid'])
        return mail

    def remove_mail(self, mid):
        return self.db.execute("DELETE FROM `%s` "
                               "WHERE mid=%%s" % self._index_table,
                               mid)

    def remove_mail_range(self, touserid, start, end):
        return self.db.execute("DELETE FROM `%s` "
                               "WHERE touserid=%%s "
                               "AND mid>=%%s AND mid<=%%s AND flag=0" % self._index_table,
                               touserid, start, end)

    def get_mail_loader(self, userid):
        sql = "SELECT * FROM `%s` WHERE touserid='%s' ORDER BY mid LIMIT %%s, %%s" % (
            self._index_table, userid)
        func = self.db.query
        wrapper = with_index
        return lambda o,l : wrapper(func(sql, o, l), o)

    def get_topic_mail_loader(self, userid):
        sql = "SELECT * FROM `%s` WHERE touserid='%s' ORDER BY tid, mid LIMIT %%s, %%s" % (
            self._index_table, userid)
        func = self.db.query
        wrapper = with_index
        return lambda o,l : wrapper(func(sql, o, l), o)

    def get_mail_counter(self, userid):
        sql = "SELECT count(*) as sum FROM `%s` WHERE touserid='%s'" % (
            self._index_table, userid)
        func = self.db.get
        return lambda : func(sql)['sum']

    def get_mail(self, userid, start, limit):
        return self.db.query("SELECT * FROM `%s` "
                                 "WHERE touserid=%%s "
                                 "ORDER BY mid "
                                 "LIMIT %%s,%%s" % (self._index_table), userid,
                                 start, limit)
    
    def get_mail_simple(self, userid, start, limit):
        return self.db.query("SELECT title,mid,sendtime,readmark FROM `%s` "
                                 "WHERE touserid=%%s "
                                 "ORDER BY mid "
                                 "LIMIT %%s,%%s" % (self._index_table), userid,
                                 start, limit)

    def get_mid_rank(self, touserid, mid):
        return self.db.get('SELECT count(*) as sum '
                           'FROM `%s` '
                           'WHERE mid<%%s AND touserid=%%s '
                           'ORDER BY mid' % self._index_table,
                           mid, touserid)['sum']

    def get_first_unread(self, touserid):
        return self.db.get('SELECT count(*) '
                           'FROM `%s` '
                           'WHERE mid < ( '
                           '    SELECT mid FROM `%s` WHERE touserid=%%s '
                           '    AND readmark=0 ORDER BY mid LIMIT 1 )' % (\
                self._index_table, self._index_table), touserid)['count(*)']

    def rank2mid(self, touserid, rank):
        res = self.db.get("SELECT mid "
                          "WHERE touser=%%s ORDER BY mid "
                          "LIMIT %s, 1" % self._index_table,
                          touserid, rank)

    def get_topic_mid_rank(self, touserid, mid):
        return self.db.get('SELECT count(*) as sum '
                           'FROM `%s` '
                           'WHERE mid<%%s AND touserid=%%s '
                           'ORDER BY tid, mid' % self._index_table,
                           mid, touserid)['sum']

    def get_mail_loader_signle(self, touserid):
        sql_next = "SELECT * FROM `%s` WHERE touserid = '%s' AND mid > %%s ORDER BY mid LIMIT 1" % \
                    (self._index_table, touserid)
        sql_prev = "SELECT * FROm `%s` WHERE touserid = '%s' AND mid < %%s ORDER BY mid DESC LIMIT 1" %\
                (self._index_table, touserid)
        fun = self.db.get
        return (lambda mid : fun(sql_next, mid),
                lambda mid : fun(sql_prev, mid))

    def get_topic_loader_signle(self, touserid):
        sql_next = "SELECT * FROM `%s` WHERE touserid = '%s' AND mid > %%s ORDER BY tid, mid LIMIT 1" %\
                (self._index_table, touserid)
        sql_prev = "SELECT * FROm `%s` WHERE touserid = '%s' AND mid < %%s ORDER BY tid, mid DESC LIMIT 1" %\
                (self._index_table, touserid)
        fun = self.db.get
        return (lambda mid : fun(sql_next, mid),
                lambda mid : fun(sql_prev, mid))

    def one_mail(self, mid):
        return self.table_get_by_key(self._index_table, 'mid', mid)

    def get_mail_total(self, touserid):
        res = self.db.get("SELECT count(mid) as total FROM `%s` WHERE touserid = %%s" %\
                self._index_table, touserid)
        r = res.get('total')
        return int(r) if r else 0

    def prev_mail(self, userid, mid):
        return self.db.get("SELECT * FROM `%s` WHERE touserid = %%s AND mid < %%s ORDER BY mid DESC LIMIT 1" %\
                               self._index_table, userid, mid)

    def next_mail(self, userid, mid):
        return self.db.get("SELECT * FROM `%s` WHERE touserid = %%s AND mid > %%s ORDER BY mid LIMIT 1" %\
                               self._index_table, userid, mid)

    def get_new_mail(self, touserid, num, limit):
        return self.db.execute("SELECT * FROM `%s` WHERE touserid = %%s AND readmark = 0" %
                         self._index_table, touserid)

    
    def get_last_mid(self, touserid):
        res = self.db.get("SELECT max(mid) as maxid FROM `%s` WHERE touserid=%%s" % self._index_table, touserid)
        r = res.get('maxid')
        return int(r) if r else 0

    def del_mail(self, mid):
        return self.table_delete_by_key(self._index_table, 'mid',mid)

    def update_mail(self, mid, **kwargs):
        return self.table_update_by_key(self._index_table, 'mid', mid, kwargs)

    def set_read(self, uid, mid):
        # old version that need to be clean
        sql = "UPDATE `%s` SET readmark = readmark | 1 WHERE mid = %%s" %\
            self._index_table
        self.db.execute(sql, mid)

    def set_mail_read(self, mid):
        sql = "UPDATE `%s` SET readmark = readmark | 1 WHERE mid = %%s" %\
            self._index_table
        self.db.execute(sql, mid)

    def set_reply(self, mid):
        sql = "UPDATE `%s` SET readmark = readmark | 3 WHERE mid = %%s" %\
            self._index_table
        self.db.execute(sql, mid)

class Disgest(Model):

    u'''
    low level operation of disgest.
    db : argo_annhead_$boardname
    '''

    _prefix = 'argo_annhead_'

    def __(self, boardname):
        return self._prefix + boardname

    def _create_table(self, boardname, **kwargs):
        #################################
        import config
        from string import Template
        with open(config.SQL_TPL_DIR + 'template/argo_annhead.sql') as f :
            board_template = Template(f.read())
            self.execute_paragraph(board_template.substitute(boardname=boardname))

    def get_children(self, boardname, partent):
        return self.db.query("SELECT * FROM `%s` WHERE pid=%%s ORDER BY rank " % self.__(boardname),
                             partent)

    def get_node(self, boardname, nodeid):
        return self.db.get("SELECT * FROM `%s` WHERE id=%%s" % self.__(boardname),
                           nodeid)

    def get_children_and_tabs(self, boardname, partent):
        children = self.get_children(boardname, partent)
        for node in children:
            if node.title == 'README':
                return (children, node)
        else:
            return (children, None)

    def get_max_rank(self, boardname, partent):
        res = self.db.get("SELECT max(rank) FROM `%s` WHERE pid=%%s" % self.__(boardname),
                           partent)
        return res and (res['max(rank)'] or 0)

    def add_node_r(self, boardname, partent, rank, **kwargs):
        kwargs['pid'] = partent
        kwargs['rank'] = rank
        return self.table_insert(self.__(boardname), kwargs)

    def add_node(self, boardname, partent, **kwargs):
        rank = self.get_max_rank(boardname, partent) + 1
        return self.add_node_r(boardname, partent, rank, **kwargs)

    def delete_node(self, boardname, nodeid):
        return self.table_delete_by_key(self.__(boardname), 'id', nodeid)

    def swap_rank(self, boardname, node1, node2):
        r1 = node1.rank
        r2 = node2.rank
        sql = "UPDATE `%s` SET rank=%%s WHERE id=%%s" % self.__(boardname)
        return self.db.executemany(sql, ((r1, node2['id']), (r2, node1['id'])))

    def get_node_cc(self, srcboard, nodeid):
        return self.db.get("SELECT title,owner,flag,tags,content FROM %s WHERE id=%%s"%self.__(srcboard),
                           nodeid)

    # def walk_tree(self, boardname, nodeid):
    #     acc = []
    #     def walk(rootid):
    #         acc.append(rootid)
    #         children = self.db.get_children(boardname, rootid)
    #         for child in children :
    #             walk(child.id)
    #     walk(nodeid)
    #     return acc

    # def get_tree(self, boardname, node):
    #     def get_board_tree(node):
    #         if node.flag == 1:
    #             children = self.get_children(boardname, node['id'])
    #             children_tree = map(get_board_tree, children)
    #             return (node, children_tree)
    #         else:
    #             return (node, None)
    #     return get_board_tree(node)

    # def insert_tree(self, boardname, partentid, nodetree):
    #     node, children = nodetree
    #     res = self.add_node(boardname, partentid, **node)
    #     if children :
    #         for child in children:
    #             self.insert_tree(boardname, node['id'], child)
    #     return res

    # def delete_tree(self, boardname, nodeid):
    #     children = self.get_children(nodeid)
    #     if children:
    #         for child in children:
    #             self.delete_tree(boardname, child)
    #     self.delete_node(boardname, nodeid)

    # def copy_node(self, srcboard, nodeid, descboard, partentid, **kwargs):
    #     res = self.get_node_cc(srcboard, nodeid)
    #     res['rank'] = self.get_max_rank(self.__(descboard), partentid)
    #     res.update(kwargs)
    #     new_nodeid = self.table_insert(self.__(descboard), res)

    #     if res.flag == 1:
    #         for child in self.get_children(srcboard, nodeid):
    #             self.copy_node(srcboard, child.id,
    #                            descboard, new_nodeid)            
    #     else:
    #         return new_nodeid

class ReadMark(Model):

    u'''
    Implement the read/unread mark.
    It use a smart algorithm.

        https://github.com/argolab/argon/wiki/%E7%89%9BB%E9%97%AA%E9%97%AA%E7%9A%84%E6%9C%AA%E8%AF%BB%E6%A0%87%E8%AE%B0%E7%9A%84%E5%AE%9E%E7%8E%B0

    ch:  {order set} argo:readmark:%boardname:$userid [pid] ==> pid
    '''

    keyf = "argo:readmark:%s:%s"

    limit_max = 200

    def __(self,userid,boardname):
        return self.keyf%(userid,boardname)

    def __init__(self, manager):
        super(ReadMark, self).__init__(manager)
        self.post = manager.get_module('post')
        self.board = manager.get_module('board')

    def _is_read(self, key, pid):
        # Empty record, not read
        # And play a trick here, add -1 into read mark
        if self.ch.zcard(key) == 0:
            self.ch.zadd(key, -1, -1)
            return 0
        res = self.ch.zcount(key, pid, pid)
        if res: return res
        # If pid is smaller the oldest one in read record, mark as read
        first_pid = self.ch.zrange(key, 0, 0)[0]
        return pid < int(first_pid)

    def is_read(self,userid,boardname,pid):
        key = self.keyf % (userid, boardname)
        return self._is_read(key, pid)

    def wrapper_post_with_readmark(self, posts, boardname, userid):
        key = self.keyf%(userid, boardname)
        for p in posts :
            p['read'] = self._is_read(key, p['pid'])

    def is_new_board(self, userid, bid, boardname):
        lastpid = self.post.get_last_pid(bid)
        return lastpid is not None and not self.is_read(userid, boardname,
                                                        lastpid)

    def set_read(self,userid,boardname,pid):
        if self.is_read(userid, boardname, pid):
            return
        key = self.keyf%(userid,boardname)
        read_num = self.ch.zcard(key)
        if read_num >= self.limit_max:
            # Flush the oldest
            self.ch.zremrangebyrank(key, 0, self.limit_max - read_num )
        return self.ch.zadd(key,pid,pid)

    def clear_unread(self, userid, boardname, last):
        key = self.keyf%(userid,boardname)
        self.ch.delete(key)
        self.ch.zadd(key, last, last)

    def get_first_read(self, userid, boardname):
        d = self.ch.zrange(self.__(userid, boardname), 0, 0)
        return d and d[0]

    def get_user_read(self, userid, boardname, num):
        return self.ch.zrange(self.__(userid, boardname),-num,-1) 

class UserSign(Model):

    u'''
    About user's Signature File.
    ch : {list} argo:usersign:%userid
    '''

    keyf = "argo:usersign:%s"

    def set_sign(self,userid,data):
        assert all(map(lambda x :isinstance(x, unicode), data))
        key = self.keyf % userid
        if len(data) >= 20 :
            data = data[:20]
        self.ch.delete(key)
        self.ch.rpush(key,*data)

    def get_all_sign(self,userid):
        key = self.keyf % userid
        s = self.ch.lrange(key,0,-1)
        return map(self.u, s)

    def get_sign(self,userid,index):
        key = self.keyf % userid
        return utf8(self.ch.lindex(key,index))

    def get_random(self,userid):
        key = self.keyf % userid
        l = self.ch.llen(key)
        i = self.ch.lindex(key,random.randint(0,l-1))
        return utf8(self.ch.lindex(key,i))

    def get_sign_num(self,userid):
        key = self.keyf % userid
        return self.ch.llen(key)

class Team(Model):

    u'''
    About the team.

    ch : {set} argo:team_ust:$userid ==> team set
         {set} argo:team_tsm:$team ==> member set
    '''

    key_ust = 'argo:team_ust:%s' # User's team
    key_tsm = 'argo:team_tsm:%s' # Team's member

    key_name = 'argo:team_name'  # hash(key_name, teamid)  !! Primary
    key_mark = 'argo:team_all' # All Team, save a mark
    # key_owner = 'argo:team_owner' # hash(key_name, teamowner)
    key_publish = 'argo:team_publish'  # All the publish team
    
    # Base

    def all_team(self):
        return map(self.u, self.ch.hkeys(self.key_name))

    def register_team(self, teamid, teamname, publish):
        self.ch.hset(self.key_name, teamid, teamname)
        if publish :
            self.publish(teamid)

    def confirm_exists(self, teamid):
        if not self.exists(teamid):
            raise ValueError(u'No such team [%s]' % teamid)

    def drop_team(self, teamid):
        self.ch.hdel(self.key_name, teamid)
        self.ch.delete(self.key_ust % teamid)
        self.ch.delete(self.key_tsm % teamid)
        self.ch.hdel(self.key_mark, teamid)
        self.ch.publish(self.key_mark, teamid)

    def exists(self, teamid):
        return self.ch.hexists(self.key_name, teamid)

    def publish(self, teamid):
        self.ch.sadd(self.key_publish, teamid)

    def unpublish(self, teamid):
        self.ch.srem(self.key_publish, teamid)        

    def join_team(self, userid, teamname):
        self.ch.sadd(self.key_ust%userid, teamname)
        self.ch.sadd(self.key_tsm%teamname, userid)

    def remove_team(self, userid, teamname):
        self.ch.srem(self.key_ust%userid, teamname)
        self.ch.srem(self.key_tsm%teamname, userid)

    def is_in_team(self, userid, teamname):
        return self.ch.sismenber(self.key_tsm%teamname,
                                 userid)

    def all_members(self, teamname):
        return self.ch.smembers(self.key_tsm%teamname)

    def user_teams(self, userid):
        return self.ch.smembers(self.key_ust%userid)

    def get_names(self, *teamid):
        return map( lambda x : utf8(self.ch.hget(self.key_name, x)), teamid)

class Permissions(Model):

    u'''
    About the Permissions.

    ch : {set} argo:perm_glb:$permname ==> team set
         {set} argo:perm_brd:$boardname:$permname ==> team set
    '''
    
    key_glb = 'argo:perm_glb:%s'    # Global Permissions
    key_brd = 'argo:perm_brd:%s:%s' # Board's Permissions
    # key_tsp = 'argo:perm_tsp:%s:%s' # Team's Permissions
    key_ust = Team.key_ust

    # Global Permissions

    def give_perm(self, perm, *teamname):
        self.ch.sadd(self.key_glb%perm, *teamname)

    def remove_perm(self, teamname, *perm):
        self.ch.srem(self.key_glb%perm, *teamname)

    def check_perm(self, userid, perm):
        return self.ch.sinter(self.key_ust%userid, self.key_glb%perm)

    def clear_perm(self, perm):
        self.ch.delete(self.key_glb%perm)

    def get_teams_with_perm(self, perm):
        return set(utf8(m) for m in self.ch.smembers(self.key_glb%perm))

    # Board Permissions

    def give_boardperm(self, boardname, perm, *teamname):
        self.ch.sadd(self.key_brd%(boardname, perm), *teamname)

    def remove_boardperm(self, boardname, perm, *teamname):
        self.ch.srem(self.key_brd%(boardname, perm), *teamname)

    def clear_boardperm(self, boardname, perm):
        self.ch.delete(self.key_brd%(boardname, perm))

    def check_boardperm(self, userid, boardname, perm):
        return self.ch.sinter(self.key_ust%userid,
                              self.key_brd%(boardname, perm))

    def checkmany_boardperm(self, userid, boardname, *perms):
        key = self.key_ust%userid
        return map(lambda p : bool(self.ch.sinter(key, self.key_brd%(boardname, p))),
                   perms)

    def check_boardperm_team(self, teamname, boardname, perm):
        return self.ch.sismember(self.key_brd%(boardname, perm), teamname)

    def get_teams_with_boardperm(self, boardname, perm):
        return set( utf8(m) for m in self.ch.smembers(self.key_brd%(boardname, perm)))

class Clipboard(Model):

    u'''
    About the clipboard.

    ch : argo:clipboard:%userid
    '''

    keyf = 'argo:clipboard:%s'
    max_len = 100000
    
    def set_clipboard(self, userid, value=''):
        key = self.keyf % userid
        self.ch.set(key, value)

    def append_clipboard(self, userid, value):
        key = self.keyf % userid
        l = self.ch.strlen(userid)
        if l + len(value) > self.max_len :
            return False
        self.ch.append(key, value)

    def get_clipboard(self, userid):
        key = self.keyf % userid
        return utf8(self.ch.get(key))

class AuthUser(dict):
    def __getattr__(self, name):
        return super(AuthUser,self).get(name)
    def __setattr__(self,name,value):
        self[name] = value

class UserAuth(Model):

    u'''
    An high level module to deal with auth.

    using mod:  userinfo, status, userperm
    '''
    
    ban_userid = ['guest','new']
    GUEST = AuthUser(userid='guest',is_first_login=None)

    def __init__(self, manager):
        super(UserAuth, self).__init__(manager)
        self.userinfo = manager.get_module('userinfo')
        self.status = manager.get_module('status')
        self.userperm = manager.get_module('userperm')
        self.favourite = manager.get_module('favourite')
        self.team = manager.get_module('team')
        
    def gen_passwd(self,passwd):
        return bcrypt.hashpw(passwd, bcrypt.gensalt(10))

    def set_passwd(self, userid, passwd):
        self.userinfo.update_user(userid, passwd=self.gen_passwd(passwd))

    def check_passwd_match(self,passwd,code):
        try:
            return bcrypt.hashpw(passwd, code) == code
        except:
            return False

    def user_exists(self,userid):
        try:
            return bool(self.userinfo.name2id(userid))
        except:
            return False        

    def check_userid(self, userid):
        if len(userid) < 3:
            raise RegistedError(u'此id过短，请至少3个字符以上')
        if userid in self.ban_userid :
            raise RegistedError(u'此id禁止注册')
        if self.user_exists(userid):
            raise RegistedError(u'此帐号已被使用')

    def register(self, userid, passwd, **kwargs):
        self.userinfo.add_user(
            userid=userid,
            passwd=self.gen_passwd(passwd),
            nickname=userid,
            **kwargs
            )
        self.favourite.init_user_favourite(userid)
        self.userperm.init_user_team(userid)
        
    def get_guest(self):
        return self.GUEST

    def login_http(self, userid, passwd, host):

        code = self.userinfo.select_attr(userid, "userid, passwd")
        if code is None:
            raise LoginError(u'没有该用户!')
        code = code['passwd']

        if not self.check_passwd_match(passwd, code):
            raise LoginError(u'账号和密码不匹配！')

        self.userinfo.update_user(userid,
                                  lasthost=host,
                                  lastlogin=datetime.now())
        res = self.userinfo.get_user(userid)
        return res['userid']

    def login(self, userid, passwd, host, session=True):

        if userid == 'guest':
            raise LoginError(LoginError.NO_SUCH_USER) # Not such user self.get_guest()

        # user_exist
        code = self.userinfo.select_attr(userid,"passwd")
        if code is None :
            raise LoginError(u'没有该用户！')
        code = code['passwd']

        #check_password
        if not self.check_passwd_match(passwd,code):
            raise LoginError(u'帐号和密码不匹配！')
        self.userinfo.update_user(userid,
                               lasthost=host,
                               lastlogin=datetime.now())
        res = self.userinfo.get_user(userid)
        res.is_first_login = res['firstlogin'] == 0

        userid = res['userid']

        if session:
            #set_state
            seid = self.status.new_session(host, userid, status.LOGIN,
                                           ord(userid[0]))
            if seid is False :
                return LoginError(u'已达最大上线数！')
            res.seid = seid

        if res['userid'] == 'argo' :
            res['is_admin'] = True

        self.msg('Coming :: %s,%s,%s' % (userid,passwd,host))
        self.msg(datetime.now().ctime())

        # print res.seid
        return res

    def msg(self,string):
        print string

    def logout(self, seid):
        self.status.logout(seid)

    def safe_logout(self,seid):
        try:
            self.logout(seid)
        except:
            pass

class Notify(Model):

    _mail = 'argo:notify_mail'
    _notice = 'argo:notify_notice'
    
    def add_mail_notify(self, userid):
        self.ch.hincrby(self._mail, userid)

    def add_notice_notify(self, userid):
        self.ch.hincrby(self._notice, userid)

    def clear_mail_notify(self, userid):
        self.ch.hdel(self._mail, userid)

    def clear_notice_notify(self, userid):
        self.ch.hdel(self._notice, userid)

    def check_mail_notify(self, userid):
        return self.ch.hget(self._mail, userid)

    def check_notice_notify(self, userid):
        return self.ch.hget(self._notice, userid)

class Notice(Model):

    _notice = 'argo:notice:%s'

    max_num = 100

    NOTICE_REPLY = 'r' # r:userid:boardname:pid
    NOTICE_INVE = '@'
    NOTICE_ADDF = 'f'

    def add_notice(self, userid, *args):
        key = self._notice % userid
        self.ch.lpush(key, ':'.join(args))
        self.ch.ltrim(key, 0, self.max_num)

    def get_notice(self, userid, start, limit):
        return map(lambda x : x.split(':'),
                   self.ch.lrange(self._notice % userid,
                                  start, start+limit))

    def add_inve(self, sponer, boardname, pid, userids):
        notice = '@:%s:%s:%s' % (sponer, boardname, pid)
        for u in userids:
            key = self._notice % u
            self.ch.lpush(key, notice)
            self.ch.ltrim(key, 0, self.max_num)

class Action(Model):

    u'''
    High level operation about user's action.
    using mod: board, status, post, mail, userinfo
    '''

    def __init__(self, manager):
        super(Action, self).__init__(manager)
        self.board = manager.get_module('board')
        self.status = manager.get_module('status')
        self.post = manager.get_module('post')
        self.mail = manager.get_module('mail')
        self.userinfo = manager.get_module('userinfo')
        self.readmark = manager.get_module('readmark')
        self.notify = manager.get_module('notify')
        
    def enter_board(self,sessionid,boardname):
        self.status.enter_board(boardname)

    def exit_board(self,sessionid,boardname):
        self.status.exit_board(boardname)

    def new_post(self,boardname,userid,title,content,
                 addr,host,replyable,signature=''):
        bid = self.board.name2id(boardname)
        pid = self.post.add_post(
            bid=bid,
            owner=userid,
            title=title,
            content=content,
            replyid=0,
            fromaddr=addr,
            fromhost=host,
            replyable=replyable,
            signature=signature,
            )
        #print ('pid', pid)
        self.post.update_post(pid,tid=pid)
        # self.board.update_attr_plus1(bid,'total')
        # self.board.update_attr_plus1(bid,'topic_total')
        self.readmark.set_read(userid, boardname, pid)
        return pid
    
    def reply_post(self,boardname,userid,title,content,addr,
                   host,replyid,replyable = 1,signature = ''):
        post = self.post.get_post(replyid)
        tid = post['tid']
        bid = self.board.name2id(boardname)
        pid = self.post.add_post(
            owner=userid,
            title=title,
            bid=bid,
            content=content,
            replyid=replyid,
            fromaddr=addr,
            fromhost=host,
            tid=tid,
            replyable=replyable,
            signature=signature,
            )
        # self.board.update_attr_plus1(bid,'total')
        self.readmark.set_read(userid, boardname, pid)
        # if post['look_reply'] and self.userinfo.user_exist(post['owner']):
        #     self.notice.add_notice(post['owner'],
        #                            Notice.NOTICE_REPLY,
        #                            userid,
        #                            boardname,
        #                            pid)
        #     self.notify.add_notice_notify(post['owner'])
        return pid

    def update_post(self,userid,pid,content):
        return self.post.update_post(pid,
                              owner = userid,
                              content=content)

    def update_title(self, userid, pid, new_title):
        return self.post.update_post(pid, title=new_title)

    def has_edit_title_perm(self, userid, pid):
        post = self.post.get_post(pid)
        return post['real_owner'] == userid


    def send_mail(self, fromuserid, touserid, **kwargs):
        mid =  self.mail.send_mail(fromuserid=fromuserid,
                                   touserid=touserid,
                                   replyid=0,
                                   **kwargs)
        self.mail.update_mail(mid, tid=mid)
        self.notify.add_mail_notify(touserid)
        return mid

    def reply_mail(self, userid, old_mail, **kwargs):
        res = self.mail.send_mail( fromuserid=userid,
                                   touserid=old_mail['fromuserid'],
                                   tid=old_mail['tid'],
                                   replyid=old_mail['mid'],
                                   **kwargs)
        self.mail.set_reply(old_mail['mid'])
        self.notify.add_mail_notify(old_mail['fromuserid'])
        return res

    def del_mail(self, mid):
        return self.mail.del_mail(mid)

    def get_mail(self, userid, num, limit, touid=None):
        return self.mail.get_mail(userid, num, limit)

    def get_new_mail(self, userid, num, limit):
        return self.mail.get_new_mail(userid, num, limit)

    def one_mail(self, mid):
        return self.mail.one_mail(mid)


class Admin(Model):

    u'''
    High level operation about content admin.
    using mod: board, userperm, post, section
    '''

    def __init__(self, manager):
        super(Admin, self).__init__(manager)
        self.board = manager.get_module('board')
        self.userperm = manager.get_module('userperm')
        self.post = manager.get_module('post')
        self.section = manager.get_module('section')
        self.deny = manager.get_module('deny')
        self.userinfo = manager.get_module('userinfo')
        self.mail = manager.get_module('mail')

    def set_post_replyattr(self,userid, pid, replyable):
        self.post.update_post(pid, replyable=replyable)

    def add_board(self, userid, boardname, sid, description, allowteam, postteam, denyteam, adminteam):
        self.board.add_board(boardname=boardname, description=description, sid=sid)
        self.userperm.init_boardteam(boardname)
        self.userperm.set_board_allow(boardname, allowteam)
        self.userperm.set_board_post(boardname, postteam)
        self.userperm.set_board_deny(boardname, denyteam)
        self.userperm.set_board_admin(boardname, adminteam)

    def update_board(self, userid, bid, boardname, sid, description, is_open, is_openw):
        self.board.update_board(bid, boardname=boardname,
                                description=description, sid=sid)
        self.userperm.init_board_team(boardname, is_open, is_openw)

    def join_bm(self, owner, userid, boardname):
        bms = self.board.get_board_bm(boardname)
        if userid in bms:
            raise ValueError(u'%s已经是%s版主'%(userid, boardname))
        bms.append(userid)
        self.board.set_board_bm(boardname, bms)
        self.userperm.join_board_bm(boardname, userid)

    def remove_bm(self, owner, userid, boardname):
        bms = self.board.get_board_bm(boardname)
        if userid not in bms:
            raise ValueError(u'%s不是%s版主'%(userid, boardname))
        bms.remove(userid)
        self.board.set_board_bm(boardname, bms)
        self.userperm.join_board_bm(boardname, userid)

    def set_g_mark(self, userid, board, post):
        if board['perm'][3] :
            post['mark_g'] = not post['mark_g']
            self.post.update_post( post['pid'], mark_g=post['mark_g'])
        return post

    def set_m_mark(self, userid, board, post):
        if board['perm'][3] :
            post['mark_m'] = not post['mark_m']
            self.post.update_post( post['pid'], mark_m=post['mark_m'])
        return post

    def remove_post_junk(self, userid, pid):
        self.post.remove_post_junk(pid)

    def remove_post_junk_range(self, userid, boardname, start, end):
        self.post.remove_post_junk_range(start, end)

    def send_system_mail(self, touserid, **kwargs):
        touid = self.userinfo.name2id(touserid)
        mid =  self.mail.send_mail(touid,
                                   fromuserid=u'deliver',
                                   touserid=touserid,
                                   replyid=0,
                                   **kwargs)
        self.mail.update_mail(touid, mid, tid=mid)
        return mid

    def deny_user(self, executor, userid, boardname, why, denytime, freetime):
        self.userperm.set_deny(boardname, userid)
        self.deny.deny_user_board(executor, userid, boardname, why, denytime, freetime)
        self.send_system_mail(userid, title=u'%s被 取消在 %s 版的发文权利' % (userid, boardname),
                              content=u"封禁原因 %s , \r\n解封日期 %s " % (why, freetime))

    def undeny_user(self, userid, boardname):
        self.userperm.remove_deny(boardname, userid)
        self.deny.remove_user_deny(userid=userid, boardname=boardname)
        self.send_system_mail(userid, title=u'恢复 %s 在 %s 的发文权利' % (userid, boardname),
                              content=u'你已经被恢复在 %s 版的发文权利' % boardname)

class Deny(Model):

    _d = "argo_denylist"
    _u = "argo_undenylist"

    def get_deny(self, userid, boardname):
        return self.db.get("SELECT * FROM `%s` WHERE userid=%%s AND boardname=%%s" % self._d ,
                           userid, boardname)

    def get_denys(self, boardname, start, limit):
        return self.db.query("SELECT * FROM `%s` "
                             "WHERE boardname=%%s "
                             "ORDER BY id LIMIT %%s,%%s" % self._d,
                             boardname, start, limit)

    def deny_user_board(self, executor, userid, boardname, why, denytime, freetime):
        return self.table_insert(self._d, dict(executor=executor, userid=userid,
                                               why=why, boardname=boardname,
                                               denytime=denytime, freetime=freetime))

    def remove_user_deny(self, userid, boardname):
        record = self.get_deny(userid, boardname)
        if not record:
            raise ValueError(u'Not such deny record. [U]{%s} [B]{%s}' % (userid, boardname))
        self.table_insert(self._u, record)
        self.table_delete_by_key(self._d, 'id', record['id'])

class Query(Model):

    u'''
    High level operation about query content.
    using mod: board, userperm, perm, favourite, section, post, userinfo
    '''

    def __init__(self, manager):
        super(Query, self).__init__(manager)
        self.board = manager.get_module('board')
        self.userperm = manager.get_module('userperm')
        self.perm = manager.get_module('perm')
        self.favourite = manager.get_module('favourite')
        self.section = manager.get_module('section')
        self.post = manager.get_module('post')
        self.userinfo = manager.get_module('userinfo')
        self.team = manager.get_module('team')

    def _wrap_boards(self, userid, boards):
        rboards = []
        for board in boards:
            board['perm'] = self.userperm.get_board_ability(userid,
                                                            board['boardname'])
            if board.perm[0] :
                rboards.append(board)
        return rboards

    def get_board_ability(self, userid, boardname):
        return self.userperm.get_board_ability(userid, boardname)

    def get_boards(self, userid, sid=None):
        if sid is None :
            boards = self.board.get_all_boards()
        else:
            boards = self.board.get_by_sid(sid)
        return self._wrap_boards(userid, boards)

    def get_board_by_name(self, userid, boardname):
        return self.board.get_board(boardname)

    def get_all_favourite(self, userid):
        bids = self.favourite.get_all(userid)
        boards = map(lambda d: self.board.get_board_by_id(d), bids)
        return self._wrap_boards(userid, boards)

    def get_section(self, sid):
        return self.section.get_section_by_sid(sid)

    def get_all_section(self):
        return self.section.get_all_section()

    def get_board(self, userid, boardname):
        return self.board.get_board(boardname)

    def get_all_section_with_rownum(self):
        return self.section.get_all_section_with_rownum()

    def get_user(self, userid, toquery):
        base = self.userinfo.get_user(toquery)
        if base :
            base['teams'] = self.team.user_teams(userid)
        return base

class WebConfigure(Model):

    def get_billboard(self):
        return [
            {
                "src":"http://ww3.sinaimg.cn/large/6b888227jw1dwesulldlyj.jpg",
                "title":"LTaoist",
                "href":"http://l-ts.me",
                "desc":"LTaoist is a boy.",
                },
            {
                "src":"http://ww1.sinaimg.cn/crop.0.80.980.245/60941145gw1dwkzd5jcksj.jpg",
                "title":"Maple",
                "href":"http://this.ismaple.com",
                "desc":"Maple is the boardmanager of linux."
                },
            ]

    def get_topten(self):
        return self.db.query("SELECT * FROM `argo_filehead` "
                             "WHERE replyid=0 "
                             "ORDER BY pid DESC "
                             "LIMIT 10 ")

    def get_board_nav(self):
        return (
            ("推荐", ("Say", "London2012", "CS", "Linux", "Search",
                      "Parttime", "BBS_Help", "Hardware", "Offical",
                      "Lecture")),
            ("热门", ("Employee", "ArgoBridge", "Diary", "water",
                      "Love", "Mobile", "Sale", "Job", "Joke",
                      "News", "Hardware", "Stock", "EastCampus",
                      "Say", "Search")),
            )

    def get_news(self):
        return (
            {
                "title":"快参加2012年linux班聚吧！",
                "href":"l-ts.me",
                "time":"2012-07-12",
                },
            {
                "title":"站衫开始受订了咯！",
                "href":"weibo.com",
                "time":"2012-02-33",
                }
            )

class FreqControl(Model):

    u'''
    Limit the user's action frequency.
    Basic usage:

    def action(userid, *args, **kwargs):
        try:
            filter_freq_per(userid)
        except TooFrequentException:
            do_no_thing()
        else:
            do_action(userid, *args, **kwargs)

    Wrap as decorator may be good as well.

    ch : {set} argo:freqcontrol:$userid ==> user set
    
    '''

    keyf = "argo:freqcontrol:%s"

    per = 3
    mid = 15
    big = 120
    large = 900

    LOGIN = 15
    POST = 2
    SEND_MAIL = 3
    
    def _filter_freq(self, actionname, sessionid, per):
        key = self.keyf % actionname
        if self.ch.sismenber(key, sessionid) :
            return False
        if self.ch.exists(key):
            self.ch.sadd(key, userid)
        else:
            self.ch.sadd(key, userid)
            self.ch.expire(key, per)
        return True

    def filter_freq_login(self, sessionid):
        return self._filter_freq('LOGIN', sessionid, self.LOGIN)
    
    def filter_freq_post(self, sessionid):
        return self._filter_freq('POST', sessionid, self.POST)
    
    def filter_freq_send_mail(self, sessionid):
        return self._filter_freq('SEND_MAIL', sessionid, self.SEND_MAIL)

def with_index(d, start_num):
    for index in range(len(d)):
        d[index]['index'] = start_num + index
    return d

def utf8(source):
    return source.decode('utf8')

def add_column(coldef,after,*tables):
    for table in tables:
        try:
            global_conn.execute("ALTER TABLE `%s` "
                                "ADD COLUMN %s AFTER `%s`" %\
                                    (table, coldef, after))
        except Exception as e:
            print e.message

def update_all(setsql, *tables):
    for table in tables:
        global_conn.execute("UPDATE `%s` "
                            "SET %s" % (table, setsql))

def sql_all_boards(sql):
    d = Board()
    d.bind(db=global_conn)
    for table in map(lambda x : 'argo_filehead_%s' % x['boardname'],
                     d.get_all_boards()):
        try:
            global_conn.execute(sql % table)
        except Exception as e:
            traceback.print_exc()
            print '[FAIL] %s' % e.message
        else:
            print '[SUCC] %s' % (sql % table)

def foreach_board(f):
    d = Board()
    d.bind(db=global_conn)
    for board in d.get_all_boards():
        f(board)
