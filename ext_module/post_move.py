#!/usr/bin/env python

import sys
sys.path.append('..')

import chardet
from model import manager as mgr
import ext_post, time

encoding = ['gb18030', 'gbk', 'utf-8']

def ts2dt(ts):
    ltime = time.localtime(ts)
    timeStr = time.strftime("%Y-%m-%d %H:%M:%S", ltime)
    return timeStr

def decode_g2u(sstream):
    for e in encoding:
        try:
            return str(sstream).decode(e)
        except Exception, e:
            continue
    return ''

def main_process():
    boards = mgr.board.get_all_boards()
    for brd in boards:
        num = -1
        while True:
            try:
                num += 1
                try:
                    fh = ext_post.GetFileHeader('bbs_home', brd.boardname, brd.bid, num)
                except IOError, e:
                    break

                content = decode_g2u(fh.GetFileStream())
                title = decode_g2u(fh.title)
                if content == '' or title == '':
                    print 'fail %s %s' % (brd.boardname, fh.filename)

                mgr.post.add_post(bid = fh.bid,
                        owner = fh.owner,
                        realowner = fh.realowner,
                        title = title,
                        posttime = ts2dt(fh.filetime),
                        oldfilename = fh.filename,
                        content = content,
                        flag = fh.flag)
                print brd.boardname, num
            except AttributeError, e:
                print e
                break


if __name__ == '__main__':
    main_process()

