import json

from helpers import request, decorators
from models import Game
from google.appengine.ext.ndb import Key, OR, AND


class UserGamesHandler(request.RequestHandler):
    @decorators.jwt_required
    def post(self, payload):
        """
        Retrieves user's in-progress games starting from the provided offset, or 0. Limit 10
        :param payload: the JWT payload
        :return:
        """
        if self.request.body is not None:
            data = json.loads(self.request.body)
            try:
                offset = int(data.get('offset'))
            except:
                offset = 0
        else:
            offset = 0

        key = Key(urlsafe=payload.get('jwt_token'))

        try:
            games = Game.query(
                AND(
                    OR(Game.player_one == key,
                       Game.player_two == key),
                    Game.game_completed == False)).order(-Game.date_created).fetch(offset=offset, limit=10)
            return self.response.write(json.dumps([{
                                                       "player_one": game.player_one_name,
                                                       "player_two": game.player_two_name,
                                                       "game_key": game.key.urlsafe()} for game in games]))
        except:
            return self.error(500)
