import json

from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError

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
        data = json.loads(self.request.body)

        try:
            offset = int(data.get('offset'))
        except:
            offset = 0

        try:
            key = Key(urlsafe=payload.get('userKey'))
        except TypeError:
            return self.response.set_status(400, 'key was unable to be retrieved')
        except ProtocolBufferDecodeError:
            return self.response.set_status(400, 'key was unable to be retrieved')
        except Exception as e:
            return self.error(500)

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
