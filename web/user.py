from lib import BaseHandler, manager

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
