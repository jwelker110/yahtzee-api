import json
import endpoints

from protorpc import remote, message_types
from ep.endpoint_api import yahtzee_api
from messages import CancelGameRequestForm
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from helpers import token
from google.appengine.ext.ndb import Key


@yahtzee_api.api_class("game")
class CancelGameHandler(remote.Service):
    @endpoints.method(CancelGameRequestForm,
                      message_types.VoidMessage,
                      name="cancel_game",
                      path="game/forfeit")
    def cancel_game(self, request):
        """
        This will cancel the game associated with the provided game key
        :param payload: JWT payload containing the userKey
        :return: 200 if successful, otherwise a response code other than 2-- with a message
        """
        game_key = request.game_key
        payload = token.decode_jwt(request.jwt_token)

        try:
            user = Key(urlsafe=payload.get('user_key')).get()
            game = Key(urlsafe=game_key).get()
        except TypeError:
            raise endpoints.BadRequestException('key was unable to be retrieved')
        except ProtocolBufferDecodeError:
            raise endpoints.BadRequestException('key was unable to be retrieved')
        except Exception as e:
            raise endpoints.InternalServerErrorException('An error occurred when attempting to take the turn')

        if user is None or game is None:
            raise endpoints.BadRequestException('Could not locate the user and game specified')

        try:
            if game.player_one != user.key and game.player_two != user.key:
                # this isn't even the user's game!
                raise endpoints.UnauthorizedException('Can not cancel someone else\'s game')

            if game.player_one_completed is True and game.player_two_completed is True:
                raise endpoints.BadRequestException('Can not cancel a game that has already been completed')

            if game.player_one_cancelled is True or game.player_two_cancelled is True:
                raise endpoints.BadRequestException('Game has been cancelled already')

            # game has not been completed / cancelled already
            if game.player_one == user.key:
                game.player_one_cancelled = True
                game.player_two_completed = True
                player_two = game.player_two.get()
                player_two.wins += 1
                game.put()
                player_two.put()
            elif game.player_two == user.key:
                game.player_two_cancelled = True
                game.player_one_completed = True
                player_one = game.player_one.get()
                player_one.wins += 1
                game.put()
                player_one.put()

            return message_types.VoidMessage

        except Exception as e:
            # print e.message
            raise endpoints.InternalServerErrorException('An error occurred while trying to cancel the game')
