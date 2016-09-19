import webapp2
import webtest
import json
import endpoints

from ep import ViewGameHandler, CancelGameHandler
from base import GameTestCase
from models import User, Game, TurnCard
from helpers import token


class TestCaseGame(GameTestCase):

    def setUp(self):
        super(TestCaseGame, self).setUp()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        app = endpoints.api_server([
            ViewGameHandler,
            CancelGameHandler
        ], restricted=False)
        self.testapp = webtest.TestApp(app)
        self.user_one = User(username='Tester01', email='Tester01@email.com')
        self.user_two = User(username='Tester02', email='Tester02@email.com')
        self.user_one.put()
        self.user_two.put()
        self.jwt_token_player_one = token.encode_jwt({"user_key": self.user_one.key.urlsafe()})
        self.jwt_token_player_two = token.encode_jwt({"user_key": self.user_two.key.urlsafe()})
        self.jwt_token_player_three = token.encode_jwt({"user_key": '12kJ123JERW45LKJ3KJ56'})
        self.game = Game(player_one=self.user_one.key,
                         player_one_name=self.user_one.username,
                         player_two=self.user_two.key,
                         player_two_name=self.user_two.username)
        self.game.put()
        self.user_one_turncard = TurnCard(owner=self.user_one.key, game=self.game.key)
        self.user_two_turncard = TurnCard(owner=self.user_two.key, game=self.game.key)
        self.user_one_turncard.put()
        self.user_two_turncard.put()

    def tearDown(self):
        super(TestCaseGame, self).tearDown()

    def test_retrieve_game(self):
        """
        Tests retrieving details for their game
        """
        resp = self.testapp.post_json('/_ah/spi/ViewGameHandler.retrieve_game', {
            "jwt_token": self.jwt_token_player_one,
            "game_key": self.game.key.urlsafe()
        })
        resp = json.loads(resp.body)
        self.assertIsNotNone(resp['game'], 'Game details were not returned')
        self.assertIsNotNone(resp['game_key'], 'Game key was not returned')

    def test_retrieve_game_wrong_user(self):
        """
        Tests to ensure users are unable to query details about other users games
        :return:
        """
        resp = self.testapp.post_json('/_ah/spi/ViewGameHandler.view_game', {
            "jwt_token": self.jwt_token_player_three,
            "game_key": self.game.key.urlsafe()
        }, expect_errors=True)
        self.assertIn('400', resp.status, 'Did not properly handle a random string passed for key')

    def test_cancel_game_player_one(self):
        """
        Tests to ensure a user may forfeit a game
        """
        resp = self.testapp.post_json('/_ah/spi/CancelGameHandler.cancel_game', {
            "jwt_token": self.jwt_token_player_one,
            "game_key": self.game.key.urlsafe()
        })
        self.assertTrue(self.game.player_one_cancelled, 'Player One was unable to cancel the game')

    def test_cancel_game_player_two(self):
        """
        Tests to ensure a user may forfeit a game
        """
        resp = self.testapp.post_json('/_ah/spi/CancelGameHandler.cancel_game', {
            "jwt_token": self.jwt_token_player_two,
            "game_key": self.game.key.urlsafe()
        })
        self.assertTrue(self.game.player_two_cancelled, 'Player One was unable to cancel the game')
