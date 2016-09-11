import json

from helpers import request
from models import User


class AllUsersHandler(request.RequestHandler):
    def get(self):
        """
        Return 10 users. If an offset is provided, the results will be offset by the
        provided amount
        :return:
        """
        offset = self.request.get('offset')

        if offset is None or offset == '':
            offset = 0

        try:
            offset = int(offset)
        except:
            offset = 0

        try:
            users = User.query().fetch(offset=offset, limit=10)
            return self.response.write(json.dumps([{
                                                       "username": user.username,
                                                       "userKey": user.key.urlsafe()
                                                   } for user in users]))
        except Exception as e:
            print e.message
            return self.error(500)
