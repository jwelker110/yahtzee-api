import json

from helpers import request
from models import User, Game


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


class HighScoreHandler(request.RequestHandler):
    def get(self):
        """
        Retrieve the 10 users with highest scores in a single game, ordered from highest to lowest
        :return:
        """
        try:
            games = Game.query(Game.player_one_completed == True,
                               Game.player_two_completed == True).order(-Game.winner_score).fetch(limit=10)
            return self.response.write(json.dumps([{
                                                       "username": game.winner_name,
                                                       "score": game.winner_score
                                                   } for game in games]))
        except:
            return self.error(500)