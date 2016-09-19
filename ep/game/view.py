import endpoints

from protorpc import remote
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from google.appengine.ext.ndb import Key
from messages import ViewGameRequestForm, ViewGameResponseForm
from helpers import token
from ep.endpoint_api import yahtzee


@yahtzee.api_class("game")
class ViewGameHandler(remote.Service):
    @endpoints.method(ViewGameRequestForm,
                      ViewGameResponseForm,
                      name='view_game',
                      path='view')
    def retrieve_game(self, request):
        """
        JWT required. Retrieves the game matching the provided key, and returns the game details
        """
        game_key = request.game_key
        payload = token.decode_jwt(request.jwt_token)

        try:
            user = Key(urlsafe=payload.get('user_key'))
            game = Key(urlsafe=game_key).get()
        except TypeError:
            raise endpoints.BadRequestException('key was unable to be retrieved')
        except ProtocolBufferDecodeError:
            raise endpoints.BadRequestException('key was unable to be retrieved')
        except Exception as e:
            raise endpoints.InternalServerErrorException('An error occrurred while retrieving game details')

        if game is None:
            raise endpoints.BadRequestException('That game does not exist')

        # k the game exists let's make sure it's the user's game
        if game.player_one != user and game.player_two != user:
            raise endpoints.UnauthorizedException('You are not authorized to view other players games')

        return ViewGameResponseForm(
            game_key=game_key,
            game=game.to_form()
        )
