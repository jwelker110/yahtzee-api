import json

from helpers import request
from models import User


class UserRankHandler(request.RequestHandler):
    def get(self):
        """
        Retrieve the 10 users with the most wins, ordered from highest to lowest
        :return:
        """
        try:
            users = User.query().order(-User.wins).fetch(limit=10)
            return self.response.write(json.dumps([{
                                                       "username": user.username,
                                                       "wins": user.wins
                                                   } for user in users]))
        except:
            return self.error(500)
