import webapp2
import webtest
import json
import random

from helpers import request, decorators, token
from ep import UserRollHistoryHandler, UserGamesHistoryHandler, UserGamesHandler
from models import Game, TurnCard, User, Turn
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
        users = []
        for _ in xrange(0, 10):
            users.append(
                User(username='Tester %s' % (_ + 1), email='Tester@email.com', wins=random.randint(0, 10)).put())

        # loop through and make some games
        user_one = users[0].get()
        for _ in xrange(0, 5):
            user_two = users[9 - _].get()
            game = Game(player_one=user_one.key,
                         player_one_name=user_one.username,
                         player_two=user_two.key,
                         player_two_name=user_two.username,
                         player_one_upper_sub_total=random.randint(10, 80),
                         player_one_lower_total=random.randint(30, 150),
                         player_two_upper_sub_total=random.randint(10, 80),
                         player_two_lower_total=random.randint(30, 150),
                         player_one_completed=True,
                         player_two_completed=False if _ == 4 else True)
            game.put()

        resp = self.testapp.post('/api/v1/user/history', params=json.dumps({
            "jwt_token": token.encode_jwt({"userKey": user_one.key.urlsafe()})
        }))
        resp = json.loads(resp.body)
        self.assertEqual(len(resp), 4, '4 historical games were not retrieved')

    def test_retrieve_game_current(self):
        resp = self.testapp.post('/api/v1/user/current', params=json.dumps({
            "jwt_token": self.jwt_token_player_one
        }))
        resp = json.loads(resp.body)
        self.assertEqual(len(resp), 1, 'Did not return 1 current game')

    def test_retrieve_game_moves(self):
        users = []
        for _ in xrange(0, 2):
            users.append(
                User(username='Tester %s' % (_ + 1), email='Tester@email.com', wins=random.randint(0, 10)).put())

        user_one = users[0].get()
        user_two = users[1].get()

        game = Game(player_one=user_one.key,
                    player_one_name=user_one.username,
                    player_two=user_two.key,
                    player_two_name=user_two.username)
        game.put()
        user_one_turncard = TurnCard(
            owner=user_one.key,
            game=game.key
        )
        user_one_turncard.put()

        # let's take the turns
        for _ in xrange(0, 15):
            roll = []
            turn = Turn()
            for _ in xrange(0, 5):
                roll.append(random.randint(0, 6))
            turn.roll_one = roll
            roll = []
            for _ in xrange(0, 5):
                roll.append(random.randint(0, 6))
            turn.roll_two = roll
            roll[0] = random.randint(0, 6)
            turn.roll_three = roll
            turn.put()
            user_one_turncard.turns.append(turn.key)
        user_one_turncard.put()

        resp = self.testapp.post('/api/v1/game/history', params=json.dumps({
            "jwt_token": token.encode_jwt({"userKey": user_one.key.urlsafe()}),
            "game_key": game.key.urlsafe()
        }))
        resp = json.loads(resp.body)
        self.assertEqual(len(resp), 15, '15 historical turns were not retrieved')
