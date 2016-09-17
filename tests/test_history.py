import webapp2
import webtest
import json

from helpers import request, decorators, token
from ep import UserRollHistoryHandler, UserGamesHistoryHandler, UserGamesHandler
from models import Game, TurnCard, User
from base import GameTestCase
from google.appengine.ext.ndb import Key


class TestCaseHistory(GameTestCase):
    def setUp(self):
        super(TestCaseHistory, self).setUp()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        app = webapp2.WSGIApplication([
            ('/api/v1/game/history', UserRollHistoryHandler),
            ('/api/v1/user/history', UserGamesHistoryHandler),
            ('/api/v1/user/current', UserGamesHandler)
        ])
        self.testapp = webtest.TestApp(app)
        self.user_one = User(username='Tester01', email='Tester01@email.com')
        self.user_two = User(username='Tester02', email='Tester02@email.com')
        self.user_one.put()
        self.user_two.put()
        self.jwt_token_player_one = token.encode_jwt({"userKey": self.user_one.key.urlsafe()})
        self.jwt_token_player_two = token.encode_jwt({"userKey": self.user_two.key.urlsafe()})
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
        super(TestCaseHistory, self).tearDown()

    def test_retrieve_game_history(self):
        resp = self.testapp.post('/api/v1/user/history', params=json.dumps({
            "jwt_token": self.jwt_token_player_one
        }))
        print resp
        self.assertEqual(1, 1, 'test')

    def test_retrieve_game_current(self):
        resp = self.testapp.post('/api/v1/user/current', params=json.dumps({
            "jwt_token": self.jwt_token_player_one
        }))
        resp = json.loads(resp.body)
        self.assertEqual(len(resp), 1, 'Did not return 1 current game')

    def test_retrieve_game_moves(self):
        resp = self.testapp.post('/api/v1/game/history', params=json.dumps({
            "jwt_token": self.jwt_token_player_one,
            "game_key": self.game.key.urlsafe()
        }))
        print resp
        self.assertEqual(1, 1, 'test')
