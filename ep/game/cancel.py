import json

from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError

from helpers import decorators, request
from google.appengine.ext.ndb import Key


class CancelGameHandler(request.RequestHandler):
    @decorators.jwt_required
    def post(self, payload):
        """
        This will cancel the game associated with the provided game key
        :param payload: JWT payload containing the userKey
        :return: 200 if successful, otherwise a response code other than 2-- with a message
        """
        data = json.loads(self.request.body)

        try:
            user = Key(urlsafe=payload.get('userKey')).get()
            game = Key(urlsafe=data.get('gameKey')).get()
        except TypeError:
            return self.response.set_status(400, 'key was unable to be retrieved')
        except ProtocolBufferDecodeError:
            return self.response.set_status(400, 'key was unable to be retrieved')
        except Exception as e:
            return self.error(500)

        if user is None or game is None:
            return self.error(400)

        try:
            if game.player_one != user.key and game.player_two != user.key:
                # this isn't even the user's game!
                return self.response.set_status(401, 'Can not cancel someone else\'s game')

            if game.player_one_completed is True and game.player_two_completed is True:
                return self.response.set_status(400, 'Can not cancel a game that has already been completed')

            if game.player_one_cancelled is True or game.player_two_cancelled is True:
                return self.response.set_status(400, 'Game has been cancelled already')

            # game has not been completed / cancelled already
            if game.player_one == user.key:
                game.player_one_cancelled = True
                game.player_two_completed = True
                player_two = Key(game.player_two).get()
                player_two.wins += 1
                game.put()
                player_two.put()
            elif game.player_two == user.key:
                game.player_two_cancelled = True
                game.player_one_completed = True
                player_one = Key(game.player_one).get()
                player_one.wins += 1
                game.put()
                player_one.put()

            return self.response.set_status(200, 'Game cancelled')

        except:
            return self.error(500)
