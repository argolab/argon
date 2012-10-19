#!/usr/bin/env python
# encoding: utf-8
from hashlib import md5
import ext_user, time
import crypt
def main_test():
    num = -1
    while True:
        num += 1
        #if num % 100 == 0: print num
        try:
            user = ext_user.GetUserRec('PASSWDS', num)
            if user.userid == 'Cypress':
                print user.GetAddress().decode('gbk')
                print user.GetRealname().decode('gbk')
                print  user.GetUsername().decode('gbk')
                print  user.GetPasswd()

                for i in dir(user):
                    if not i.startswith('__'):
                        print i, getattr(user, i)
                break
            #if user.passwd and user.passwd[0] != '\0':
            #    print user.userid, user.GetPasswd(), user.passwd, user.GetRealname().decode('gbk'), user.lastlogin, user.email
        except AttributeError, e:
            print e
            break

if __name__ == '__main__':
    """
    旧式加密方式：
    1. 如果urec.passwd[0] == 0:
        使用DES加密方式
    2. 否则用md5:
        其中使用
        magic =" #r3:`>/CH'M&p%<xCj?bqd=/?L7o:N.s;j}Ouo!--PhX j^icU3aX{]?7`<(jOt"
        加密步骤如下：
        a = md5(magic)
        a.update(passwd)
        a.update(magic)
        a.update(userid)
        print a.hexdigest()
        注意：
            这里的userid的大小写要严格按照urec.userid来进行，否则会导致md5结果不正确。
    """
    main_test()
    userid = 'Cypress'
    passwd = ''

    print ext_user.GenPasswdMd5(userid, passwd)
    magic=" #r3:`>/CH'M&p%<xCj?bqd=/?L7o:N.s;j}Ouo!--PhX j^icU3aX{]?7`<(jOt"
    a = md5()
    a.update(magic)
    a.update(passwd)
    a.update(magic)
    a.update(userid)
    print a.hexdigest()

