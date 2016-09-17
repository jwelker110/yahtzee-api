import webapp2
import webtest
import json

from ep import TakeTurnHandler, NewTurnHandler, CompleteTurnHandler
from base import GameTestCase
from models import User, Game, TurnCard
from helpers import token


class TestCaseGame(GameTestCase):

    def setUp(self):
        super(TestCaseGame, self).setUp()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        app = webapp2.WSGIApplication([
            ('/api/v1/game/turn/complete', CompleteTurnHandler),
            ('/api/v1/game/turn/new', NewTurnHandler),
            ('/api/v1/game/turn/take', TakeTurnHandler)
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
        super(TestCaseGame, self).tearDown()

    def test_new_turn(self):
        resp = self.testapp.post('/api/v1/game/turn/new', params=json.dumps({
            "jwt_token": self.jwt_token_player_one,
            "game_key": self.game.key.urlsafe()
        }))
        resp = json.loads(str(resp.body))
        self.assertIsNotNone(resp['roll_results'])
        self.assertIsNotNone(resp['game_key'])
        self.assertIsNotNone(resp['turn_key'])
        self.assertIsNotNone(resp['turn_roll_count'])

    def test_take_turn_two(self):
        resp = self.testapp.post('/api/v1/game/turn/new', params=json.dumps({
            "jwt_token": self.jwt_token_player_one,
            "game_key": self.game.key.urlsafe()
        }))
        resp = json.loads(str(resp.body))
        # grab the turn key to send with turn request
        turn_key = resp['turn_key']
        # we're going to replace the first die in the dice
        dice_to_roll = [resp['roll_results'][0]]
        resp = self.testapp.post('/api/v1/game/turn/take', params=json.dumps({
            "jwt_token": self.jwt_token_player_one,
            "game_key": self.game.key.urlsafe(),
            "turn_key": turn_key,
            "dice_to_roll": dice_to_roll
        }))
        # grab the results of the request
        resp = json.loads(resp.body)
        self.assertIsNotNone(resp['roll_results'])
        self.assertIsNotNone(resp['game_key'])
        self.assertIsNotNone(resp['turn_key'])
        self.assertIsNotNone(resp['turn_roll_count'])
        # not really a way to check whether the roll results are different, as the roll could have been the same number
        self.assertEqual(resp['turn_roll_count'], 2, 'The turn did not count towards roll count 2')

    def test_take_turn_three(self):
        resp = self.testapp.post('/api/v1/game/turn/new', params=json.dumps({
            "jwt_token": self.jwt_token_player_one,
            "game_key": self.game.key.urlsafe()
        }))
        resp = json.loads(str(resp.body))
        # grab the turn key to send with turn request
        turn_key = resp['turn_key']
        # we're going to replace the first die in the dice
        dice_to_roll = [resp['roll_results'][0]]
        resp = self.testapp.post('/api/v1/game/turn/take', params=json.dumps({
            "jwt_token": self.jwt_token_player_one,
            "game_key": self.game.key.urlsafe(),
            "turn_key": turn_key,
            "dice_to_roll": dice_to_roll
        }))
        # grab the results of the request
        resp = json.loads(resp.body)
        # print "Roll two dice: %s" % resp['roll_results']
        # grab the turn key to send with turn request
        turn_key = resp['turn_key']
        # we're going to replace the first die in the dice
        dice_to_roll = [resp['roll_results'][0]]
        resp = self.testapp.post('/api/v1/game/turn/take', params=json.dumps({
            "jwt_token": self.jwt_token_player_one,
            "game_key": self.game.key.urlsafe(),
            "turn_key": turn_key,
            "dice_to_roll": dice_to_roll
        }))
        resp = json.loads(resp.body)
        # print "Roll three dice: %s" % resp['roll_results']
        self.assertIsNotNone(resp['roll_results'])
        self.assertIsNotNone(resp['game_key'])
        self.assertIsNotNone(resp['turn_key'])
        self.assertIsNotNone(resp['turn_roll_count'])
        self.assertEqual(resp['turn_roll_count'], 3, 'The turn did not count towards roll count 3')

    def test_take_turn_four(self):
        # this should fail!
        resp = self.testapp.post('/api/v1/game/turn/new', params=json.dumps({
            "jwt_token": self.jwt_token_player_one,
            "game_key": self.game.key.urlsafe()
        }))
        resp = json.loads(str(resp.body))
        # grab the turn key to send with turn request
        turn_key = resp['turn_key']

        # we're going to replace the first die in the dice
        dice_to_roll = [resp['roll_results'][0]]
        resp = self.testapp.post('/api/v1/game/turn/take', params=json.dumps({
            "jwt_token": self.jwt_token_player_one,
            "game_key": self.game.key.urlsafe(),
            "turn_key": turn_key,
            "dice_to_roll": dice_to_roll
        }))
        # grab the results of the request
        resp = json.loads(resp.body)
        # print "Roll two dice: %s" % resp['roll_results']
        # grab the turn key to send with turn request
        turn_key = resp['turn_key']

        # we're going to replace the first die in the dice
        dice_to_roll = [resp['roll_results'][0]]
        resp = self.testapp.post('/api/v1/game/turn/take', params=json.dumps({
            "jwt_token": self.jwt_token_player_one,
            "game_key": self.game.key.urlsafe(),
            "turn_key": turn_key,
            "dice_to_roll": dice_to_roll
        }))
        resp = json.loads(resp.body)
        # print "Roll three dice: %s" % resp['roll_results']

        # grab the turn key to send with turn request
        turn_key = resp['turn_key']
        # we're going to replace the first die in the dice
        dice_to_roll = [resp['roll_results'][0]]
        resp = self.testapp.post('/api/v1/game/turn/take', params=json.dumps({
            "jwt_token": self.jwt_token_player_one,
            "game_key": self.game.key.urlsafe(),
            "turn_key": turn_key,
            "dice_to_roll": dice_to_roll
        }), expect_errors=True)
        self.assertIn('400', resp.status, 'Did not return 400 when attempting to take more than 3 turns')

    def test_complete_turn(self):
        resp = self.testapp.post('/api/v1/game/turn/new', params=json.dumps({
            "jwt_token": self.jwt_token_player_one,
            "game_key": self.game.key.urlsafe()
        }))
        resp = json.loads(str(resp.body))
        # grab the turn key to send with turn request
        turn_key = resp['turn_key']

        # we're going to replace the first die in the dice
        dice_to_roll = [resp['roll_results'][0]]
        resp = self.testapp.post('/api/v1/game/turn/take', params=json.dumps({
            "jwt_token": self.jwt_token_player_one,
            "game_key": self.game.key.urlsafe(),
            "turn_key": turn_key,
            "dice_to_roll": dice_to_roll
        }))
        # grab the results of the request
        resp = json.loads(resp.body)
        print "Roll two dice: %s" % resp['roll_results']
        # grab the turn key to send with turn request
        turn_key = resp['turn_key']

        # we're going to replace the first die in the dice
        dice_to_roll = [resp['roll_results'][0]]
        resp = self.testapp.post('/api/v1/game/turn/take', params=json.dumps({
            "jwt_token": self.jwt_token_player_one,
            "game_key": self.game.key.urlsafe(),
            "turn_key": turn_key,
            "dice_to_roll": dice_to_roll
        }))
        resp = json.loads(resp.body)
        print "Roll three dice: %s" % resp['roll_results']
        resp = self.testapp.post('/api/v1/game/turn/complete', params=json.dumps({
            "jwt_token": self.jwt_token_player_one,
            "game_key": self.game.key.urlsafe(),
            "allocate_to": "chance"
        }))
        self.assertIsNotNone(self.game.player_one_chance, 'The turn was not added to "chance" for player one')

    def test_new_turn_after_completing_turn(self):
