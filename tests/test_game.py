import webapp2
import webtest
import json

from ep import ViewGameHandler
from base import GameTestCase
from models import User, Game, TurnCard
from helpers import token


class TestCaseGame(GameTestCase):

    def setUp(self):
        super(TestCaseGame, self).setUp()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        app = webapp2.WSGIApplication([
            ('/api/v1/game', ViewGameHandler)
        ])
        self.testapp = webtest.TestApp(app)
        self.user_one = User(username='Tester01', email='Tester01@email.com')
        self.user_two = User(username='Tester02', email='Tester02@email.com')
        self.user_one.put()
        self.user_two.put()
        self.jwt_token_player_one = token.encode_jwt({"userKey": self.user_one.key.urlsafe()})
        self.jwt_token_player_two = token.encode_jwt({"userKey": self.user_two.key.urlsafe()})
        self.jwt_token_player_three = token.encode_jwt({"userKey": '12kJ123JERW45LKJ3KJ56'})
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
        resp = self.testapp.post('/api/v1/game', params=json.dumps({
            "jwt_token": self.jwt_token_player_one,
            "game_key": self.game.key.urlsafe()
        }))
        resp = json.loads(resp.body)
        self.assertIsNotNone(resp['game'], 'Game details were not returned')
        self.assertIsNotNone(resp['game_key'], 'Game key was not returned')

    def test_retrieve_game_wrong_user(self):
        resp = self.testapp.post('/api/v1/game', params=json.dumps({
            "jwt_token": self.jwt_token_player_three,
            "game_key": self.game.key.urlsafe()
        }), expect_errors=True)
        self.assertIn('400', resp.status, 'Did not properly handle a random string passed for key')
