import json

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
        if self.request.body is not None:
            data = json.loads(self.request.body)
            try:
                offset = int(data.get('offset'))
            except:
                offset = 0
        else:
            offset = 0

        user_key = Key(urlsafe=payload.get('userKey'))

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
        user = payload.get('userKey')

        try:
            game = Key(urlsafe=game_key)
            user_key = Key(urlsafe=user)

            turncard = TurnCard.query(TurnCard.owner == user_key, TurnCard.game == game).get()

            self.response.write(json.dumps([{
                                                "roll_one": turn.roll_one,
                                                "roll_two": turn.roll_two,
                                                "roll_three": turn.roll_three,
                                                "allocated_to": turn.allocated_to,
                                                "date_completed": turn.date_completed
                                            } for turn in turncard.turns]))
        except:
            return self.error(500)
