import webtest
import json
import endpoints

from ep import TakeTurnHandler, NewTurnHandler, CompleteTurnHandler, ViewGameHandler
from ep import CreateInviteHandler, RetrieveInviteHandler, CancelInviteHandler
from base import GameTestCase
from models import User, Game, TurnCard
from helpers import token


class TestCaseGameWhole(GameTestCase):

    def setUp(self):
        super(TestCaseGameWhole, self).setUp()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        app = endpoints.api_server([
            CompleteTurnHandler,
            NewTurnHandler,
            TakeTurnHandler,
            CreateInviteHandler,
            RetrieveInviteHandler,
            CancelInviteHandler,
            ViewGameHandler
        ], restricted=False)
        self.testapp = webtest.TestApp(app)
        self.user_one = User(username='Tester01', email='Tester01@email.com')
        self.user_two = User(username='Tester02', email='Tester02@email.com')
        self.user_one.put()
        self.user_two.put()
        self.jwt_token_player_one = token.encode_jwt({"user_key": self.user_one.key.urlsafe()})
        self.jwt_token_player_two = token.encode_jwt({"user_key": self.user_two.key.urlsafe()})

    def tearDown(self):
        super(TestCaseGameWhole, self).tearDown()

    def test_whole_game(self):
        """
        Testing to ensure that a game can be created, starting with the invite, and moving all the way through 30
        turns, to the game's completion. One test to rule them all!
        :return:
        """
        resp = self.testapp.post_json('/_ah/spi/CreateInviteHandler.create_invite', {
            "jwt_token": self.jwt_token_player_one,
            "player_two_key": self.user_two.key.urlsafe()
        })
        self.assertIn('200', resp.status, '1. Could not create invite')

        resp = self.testapp.post_json('/_ah/spi/RetrieveInviteHandler.retrieve_invite', {
            "jwt_token": self.jwt_token_player_two
        })
        self.assertIn('200', resp.status, '2. Could not retrieve invite')
        resp = json.loads(resp.body)
        invite = resp['invites'][0]
        player_two_key = invite['inviter']

        resp = self.testapp.post_json('/_ah/spi/CreateInviteHandler.create_invite', {
            "jwt_token": self.jwt_token_player_two,
            "player_two_key": player_two_key
        })
        self.assertIn('200', resp.status, '3. Could not accept invite')
        resp = json.loads(resp.body)
        game_key = resp['game_key']
        game = resp['game']

        allocate_to = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes',
                       'three_of_a_kind', 'four_of_a_kind', 'full_house',
                       'small_straight', 'large_straight', 'yahtzee', 'chance']
        ###
        # loop for 15 turns!
        for _ in xrange(0, 13):
            resp = self.testapp.post_json('/_ah/spi/NewTurnHandler.new_turn', {
                "jwt_token": self.jwt_token_player_one,
                "game_key": game_key
            })
            self.assertIn('200', resp.status, '4a. Could not create new turn player one')
            resp = json.loads(resp.body)
            turn_key_player_one = resp['turn_key']
            roll_results_player_one = resp['roll_results']

            resp = self.testapp.post_json('/_ah/spi/NewTurnHandler.new_turn', {
                "jwt_token": self.jwt_token_player_two,
                "game_key": game_key
            })
            self.assertIn('200', resp.status, '4b. Could not create new turn player two')
            resp = json.loads(resp.body)
            turn_key_player_two = resp['turn_key']
            roll_results_player_two = resp['roll_results']

            ###
            # roll two
            resp = self.testapp.post_json('/_ah/spi/TakeTurnHandler.take_turn', {
                "turn_key": turn_key_player_one,
                "jwt_token": self.jwt_token_player_one,
                "game_key": game_key,
                "dice_to_roll": roll_results_player_one[:2]
            })
            self.assertIn('200', resp.status, '5a. Could not roll two player one')
            resp = json.loads(resp.body)
            roll_results_player_one = resp['roll_results']

            resp = self.testapp.post_json('/_ah/spi/TakeTurnHandler.take_turn', {
                "turn_key": turn_key_player_two,
                "jwt_token": self.jwt_token_player_two,
                "game_key": game_key,
                "dice_to_roll": roll_results_player_two[:2]
            })
            self.assertIn('200', resp.status, '5b. Could not roll two player two')
            resp = json.loads(resp.body)
            roll_results_player_two = resp['roll_results']

            ###
            # roll three
            resp = self.testapp.post_json('/_ah/spi/TakeTurnHandler.take_turn', {
                "turn_key": turn_key_player_one,
                "jwt_token": self.jwt_token_player_one,
                "game_key": game_key,
                "dice_to_roll": roll_results_player_one[:2]
            })
            self.assertIn('200', resp.status, '6a. Could not roll three player one')
            resp = json.loads(resp.body)
            roll_results_player_one = resp['roll_results']

            resp = self.testapp.post_json('/_ah/spi/TakeTurnHandler.take_turn', {
                "turn_key": turn_key_player_two,
                "jwt_token": self.jwt_token_player_two,
                "game_key": game_key,
                "dice_to_roll": roll_results_player_two[:2]
            })
            self.assertIn('200', resp.status, '6b. Could not roll three player two')
            resp = json.loads(resp.body)
            roll_results_player_two = resp['roll_results']

            ###
            # complete the turn now since we have rolled 3 times!
            resp = self.testapp.post_json('/_ah/spi/CompleteTurnHandler.complete_turn', {
                "jwt_token": self.jwt_token_player_one,
                "game_key": game_key,
                "allocate_to": allocate_to[_]
            })
            self.assertIn('200', resp.status, '7a. Could not complete turn player one')

            resp = self.testapp.post_json('/_ah/spi/CompleteTurnHandler.complete_turn', {
                "jwt_token": self.jwt_token_player_two,
                "game_key": game_key,
                "allocate_to": allocate_to[_]
            })
            self.assertIn('200', resp.status, '7b. Could not complete turn player two')

        ###
        # the game should be finished now, let's check
        resp = self.testapp.post_json('/_ah/spi/ViewGameHandler.retrieve_game', {
            "jwt_token": self.jwt_token_player_one,
            "game_key": game_key
        })
        self.assertIn('200', resp.status, '8. Could not retrieve the completed game')
        resp = json.loads(resp.body)
        print resp['game']
