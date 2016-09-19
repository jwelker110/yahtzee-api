import endpoints

from protorpc import remote, message_types
from ep.endpoint_api import yahtzee
from messages import UserGamesRequestForm, UserGamesResponseForm, UserGames
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from helpers import token
from models import Game
from google.appengine.ext.ndb import Key, OR, AND


@yahtzee.api_class("user")
class UserGamesHandler(remote.Service):
    @endpoints.method(UserGamesRequestForm,
                      UserGamesResponseForm,
                      name="retrieve_current_games",
                      path="game/current")
    def retrieve_game(self, request):
        """
        JWT required. Retrieves user's in-progress games starting from the provided offset, or 0. Limit 10
        """
        offset = request.offset
        payload = token.decode_jwt(request.jwt_token)

        try:
            key = Key(urlsafe=payload.get('user_key'))
        except TypeError:
            raise endpoints.BadRequestException('key was unable to be retrieved')
        except ProtocolBufferDecodeError:
            raise endpoints.BadRequestException('key was unable to be retrieved')
        except Exception as e:
            raise endpoints.InternalServerErrorException('An error occurred when attempting to take the turn')

        try:
            games = Game.query(
                AND(
                    OR(Game.player_one == key,
                       Game.player_two == key),
                    Game.game_completed == False)).order(-Game.date_created).fetch(offset=offset, limit=10)
            return UserGamesResponseForm(
                games=[UserGames(
                    player_one=game.player_one_name,
                    player_two=game.player_two_name,
                    game_key=game.key.urlsafe()
                ) for game in games]
            )
        except:
            raise endpoints.InternalServerErrorException('An error occurred while retrieving games')
