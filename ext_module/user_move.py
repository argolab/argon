#!/usr/bin/env python
# encoding: utf-8

import sys
sys.path.append('..')

import ext_user, bcrypt, time
from hashlib import md5
from model import manager as mgr

dec_code = 'gb18030'

def ts2dt(ts):
    ltime = time.localtime(ts)
    timeStr = time.strftime("%Y-%m-%d %H:%M:%S", ltime)
    return timeStr

def ignore_except(fun):
    try:
        return fun()
    except:
        return None

def main_process():
    recfile = 'PASSWDS'
    num = -1
    fail_cnt = 0
    fp = open('fail.lst', 'w')
    while True:
        num += 1
        try:
            urec = ext_user.GetUserRec(recfile, num)
            if not urec.userid: continue

            # Use new passwd encryption  
            user = {}
            if len(urec.GetPasswd()) > 13: # md5
                user['passwd'] = bcrypt.hashpw(urec.GetPasswd(), bcrypt.gensalt(10))
            else:
                user['passwd'] = urec.GetPasswd()

            try:
                user['firstlogin'] = ts2dt(urec.firstlogin)
                user['lastlogin'] = ts2dt(urec.lastlogin)
                user['lasthost'] = urec.lasthost
                user['lastlogout'] = ts2dt(urec.lastlogout)
                user['numlogins'] = urec.numlogins
                user['numposts'] = urec.numposts
                user['stay'] = int(urec.stay)
                user['usertitle'] = urec.usertitle
                user['gender'] = 1 if urec.gender == 'M' else 0

                user['userid'] = ignore_except(lambda : str(urec.userid).decode(dec_code))
                user['firsthost'] = ignore_except(lambda : str(urec.ident).decode(dec_code))
                user['remail'] = ignore_except(lambda : str(urec.reginfo).decode(dec_code)) #认证email
                user['username'] = ignore_except(lambda :  urec.GetUsername().decode(dec_code))
                user['email'] =ignore_except(lambda :  str(urec.email).decode(dec_code))
                user['netid'] = ignore_except(lambda :str(urec.reginfo).decode(dec_code))
                user['address'] = ignore_except(lambda :  urec.GetAddress().decode(dec_code))
                user['realname'] = ignore_except(lambda :  urec.GetRealname().decode(dec_code))
                user['birthday'] = ignore_except(lambda : time.strptime('19%d-%d-%d ' % (urec.birthyear, urec.birthmonth, urec.birthday), '%Y-%m-%d'))

                # Ignore all the None attributes
                del_att = []
                for att in user:
                    if user[att] == None:
                        del_att.append(att)

                for i in del_att: del user[i]

                mgr.userinfo.add_user( **user)

                print num, urec.userid
            except Exception, e:
                fp.write('%s %s %s %s %d\n' % (urec.userid, e, urec.ident, urec.address, urec.stay))
                fail_cnt += 1

        except AttributeError, e:
            print e
            break
    fp.close()
    print 'total fail: %d' % fail_cnt

if __name__ == '__main__':
    main_process()

