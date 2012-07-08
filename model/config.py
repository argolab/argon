# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

from argo_conf import ConfigDB,ConfigCache,ConfigBase

'''  MySQL setting '''

HOST = ConfigDB.host
PORT = ConfigDB.port
USER = ConfigDB.user
PASSWD = ConfigDB.passwd
DBNAME = ConfigDB.dbname

''' Cache settting '''

CHOST = ConfigCache.host
CPORT = ConfigCache.port


''' Other setting '''

SQL_TPL_DIR = ConfigBase.base_dir + '/argon/database/'
BASE_TABLE = [ 'attachead','boardhead','mailhead',
               'sectionhead','user','userattr']

