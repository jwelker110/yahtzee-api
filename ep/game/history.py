import endpoints

from protorpc import remote
from ep.endpoint_api import yahtzee_api
from messages import UserGamesHistoryRequestForm, UserGamesHistoryResponseForm, GamesHistory, \
    UserRollHistoryRequestForm, UserRollHistoryResponseForm, UserRollHistory
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from helpers import token
from models import Game, TurnCard
from google.appengine.ext.ndb import Key, OR, AND


@yahtzee_api.api_class("game")
class UserGamesHistoryHandler(remote.Service):
    @endpoints.method(UserGamesHistoryRequestForm,
                      UserGamesHistoryResponseForm,
                      name="games_history",
                      path="game/history")
    def games_history(self, request):
        """
        Requires JWT. Retrieves user's completed games starting from the provided offset, or 0. Limit 10
        """
        offset = request.offset
        payload = token.decode_jwt(request.jwt_token)

        try:
            user_key = Key(urlsafe=payload.get('user_key'))
        except TypeError:
            raise endpoints.BadRequestException('key was unable to be retrieved')
        except ProtocolBufferDecodeError:
            raise endpoints.BadRequestException('key was unable to be retrieved')
        except Exception as e:
            raise endpoints.InternalServerErrorException('An error occurred when attempting to take the turn')

        try:
            games = Game.query(
                AND(
                    OR(Game.player_one == user_key,
                       Game.player_two == user_key),
                    Game.game_completed == True)).order(-Game.date_created).fetch(offset=offset, limit=10)
            return UserGamesHistoryResponseForm(
                games=[GamesHistory(
                    player_one=game.player_one_name,
                    player_two=game.player_two_name,
                    game_key=game.key.urlsafe()
                ) for game in games]
            )
        except:
            raise endpoints.InternalServerErrorException('An error occurred while retrieving completed games')


@yahtzee_api.api_class("game")
class UserRollHistoryHandler(remote.Service):
    @endpoints.method(UserRollHistoryRequestForm,
                      UserRollHistoryResponseForm,
                      name="roll_history",
                      path="game/rolls")
    def roll_history(self, request):
        """
        JWT required. Retrieves user's roll history for the provided game
        """
        game_key = request.game_key
        payload = token.decode_jwt(request.jwt_token)

        try:
            game = Key(urlsafe=game_key)
            user = Key(urlsafe=payload.get('user_key'))

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
            return UserRollHistoryResponseForm(
                rolls=[UserRollHistory(
                    roll_one=turn.roll_one,
                    roll_two=turn.roll_two,
                    roll_three=turn.roll_three,
                    allocated_to=turn.allocated_to,
                    date_completed=turn.date_completed.isoformat()
                ) for turn in turns]
            )
        except TypeError:
            raise endpoints.BadRequestException('key was unable to be retrieved')
        except ProtocolBufferDecodeError:
            raise endpoints.BadRequestException('key was unable to be retrieved')
        except Exception as e:
            raise endpoints.InternalServerErrorException('An error occurred when attempting to take the turn')
