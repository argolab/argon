import os
from lib import BaseHandler, BaseFileHandler, manager

class NoticeHandler(BaseHandler):

    def get(self):
        userid = self.get_current_user()
        if not userid:
            raise tornado.web.HTTPError(404)
        total = int(manager.notify.check_notice_notify(userid) or 0)
        # manager.notify.clear_notice_notify(userid)
        notices = manager.notice.get_notice(userid, 0 , 10)
        self.srender('notify.html', notices=notices, total=total)

class UserInfoHandler(BaseHandler):

    def get(self, userid):
        user = manager.userinfo.get_user(userid)
        self.srender('user.html', user=user)

class UserAvatarHandler(BaseFileHandler):

    def head(self, userid):
        super(UserAvatarHandler, self).head('/avatar/%s'%userid)

    def get(self, userid, include_body=True):
        print os.path.join(self.root, 'avatar/%s'%userid)
        super(UserAvatarHandler, self).get('avatar/%s'%userid, include_body)

