import json

from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError

from helpers import request, decorators
from google.appengine.ext.ndb import Key


class ViewGameHandler(request.RequestHandler):
    @decorators.jwt_required
    def post(self, payload):
        """
        Retrieves the game matching the provided key, and returns the game details
        """
        data = json.loads(self.request.body)
        game_key = data.get('game_key')

        try:
            user = Key(urlsafe=payload.get('userKey'))
            game = Key(urlsafe=game_key).get()
        except TypeError:
            return self.response.set_status(400, 'key was unable to be retrieved')
        except ProtocolBufferDecodeError:
            return self.response.set_status(400, 'key was unable to be retrieved')
        except Exception as e:
            return self.error(500)

        if game is None:
            return self.response.set_status(400, 'That game does not exist')

        # k the game exists let's make sure it's the user's game
        if game.player_one != user and game.player_two != user:
            return self.response.set_status(401, 'You are not authorized to view other players games')

        return self.response.write(json.dumps({
            "game_key": game_key,
            "game": game.to_dict(exclude=['player_one',
                                          'player_two'])
        }))
