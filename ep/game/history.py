import json

from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError

from helpers import request, decorators
from models import Game, TurnCard
from google.appengine.ext.ndb import Key, OR, AND


class UserGamesHistoryHandler(request.RequestHandler):
    @decorators.jwt_required
    def post(self, payload):
        """
        Retrieves user's completed games starting from the provided offset, or 0. Limit 10
        :param payload: the JWT payload
        :return:
        """
        data = json.loads(self.request.body)

        try:
            offset = int(data.get('offset'))
        except:
            offset = 0

        try:
            user_key = Key(urlsafe=payload.get('userKey'))
        except TypeError:
            return self.response.set_status(400, 'key was unable to be retrieved')
        except ProtocolBufferDecodeError:
            return self.response.set_status(400, 'key was unable to be retrieved')
        except Exception as e:
            return self.error(500)

        try:
            games = Game.query(
                AND(
                    OR(Game.player_one == user_key,
                       Game.player_two == user_key),
                    Game.game_completed == True)).order(-Game.date_created).fetch(offset=offset, limit=10)
            return self.response.write(json.dumps([{
                                                       "player_one": game.player_one_name,
                                                       "player_two": game.player_two_name,
                                                       "game_key": game.key.urlsafe()} for game in games]))
        except:
            return self.error(500)


class UserRollHistoryHandler(request.RequestHandler):
    @decorators.jwt_required
    def post(self, payload):
        """
        Retrieves user's roll history for the provided game
        :return:
        """
        data = json.loads(self.request.body)
        game_key = data.get('game_key')

        try:
            game = Key(urlsafe=game_key)
            user = Key(urlsafe=payload.get('userKey'))

            turncard = TurnCard.query(TurnCard.owner == user, TurnCard.game == game).get()
            turns = []
            for turn in turncard.turns:
                turn = turn.get()
                turns.append({
                    "roll_one": turn.roll_one,
                    "roll_two": turn.roll_two,
                    "roll_three": turn.roll_three,
                    "allocated_to": turn.allocated_to,
                    "date_completed": turn.date_completed.isoformat()
                })
            self.response.write(json.dumps(turns))
        except TypeError:
            return self.response.set_status(400, 'key was unable to be retrieved')
        except ProtocolBufferDecodeError:
            return self.response.set_status(400, 'key was unable to be retrieved')
        except Exception as e:
            print e.message
            return self.error(500)
