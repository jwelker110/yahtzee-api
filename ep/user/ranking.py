import endpoints

from protorpc import remote, message_types
from ep.endpoint_api import yahtzee_api
from messages import UserRankResponseForm, UserHighScoreResponseForm, UserRank, UserHighScore
from models import User, Game


@yahtzee_api.api_class("user")
class UserRankHandler(remote.Service):
    @endpoints.method(message_types.VoidMessage,
                      UserRankResponseForm,
                      name="user_rank",
                      path="user/rank",
                      http_method="GET")
    def user_rank(self, request):
        """
        Retrieve the 10 users with the most wins, ordered from highest to lowest
        """
        try:
            users = User.query().order(-User.wins).fetch(limit=10)
            return UserRankResponseForm(
                players=[UserRank(
                    username=user.username,
                    wins=user.wins
                ) for user in users]
            )
        except Exception as e:
            print e.message
            raise endpoints.InternalServerErrorException('An error occurred retrieving user ranks')


@yahtzee_api.api_class("user")
class HighScoreHandler(remote.Service):
    @endpoints.method(message_types.VoidMessage,
                      UserHighScoreResponseForm,
                      name="user_score",
                      path="user/highscore",
                      http_method="GET")
    def user_score(self, request):
        """
        Retrieve the 10 users with highest scores in a single game, ordered from highest to lowest
        """
        try:
            games = Game.query(Game.player_one_completed == True,
                               Game.player_two_completed == True).order(-Game.winner_score).fetch(limit=10)
            return UserHighScoreResponseForm(
                players=[UserHighScore(
                    username=game.winner_name,
                    score=game.winner_score
                ) for game in games]
            )
        except:
            raise endpoints.InternalServerErrorException('An error occurred retrieving high scores')
