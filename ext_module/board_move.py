#!/usr/bin/env python

import sys
sys.path.append('..')

import ext_board
from model import manager as mgr

dec_code = 'gb18030'

def main_test():
    num = -1
    while True:
        num += 1
        try:
            bh = ext_board.GetBoardHeader('bbs_home/_BOARDS', num)
            if bh.boardname == '': continue
            title = str(bh.title).decode(dec_code)
            print num, bh.boardname

            mgr.board.add_board(
                    sid = 1, # Todo: fix this
                    boardname = bh.boardname,
                    description  = title,
                    bm = bh.BM,
                    flag = bh.flag,
                    lastpost = bh.lastpost)

            #for i in dir(bh):
            #    if not i.startswith('__'):
            #        if i == 'title':
            #            title = str(getattr(bh, i)).decode('gb18030')
            #            print i, title
            #        else:
            #            print i, getattr(bh, i)

        except AttributeError, e:
            print e, 'Done'
            break

if __name__ == '__main__':
    main_test()


