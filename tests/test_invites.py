import webapp2
import webtest
import json

from ep import CreateInviteHandler, RetrieveInviteHandler, CancelInviteHandler
from base import GameTestCase
from models import User, Invite
from helpers import token


class TestCaseInvites(GameTestCase):

    def setUp(self):
        super(TestCaseInvites, self).setUp()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        app = webapp2.WSGIApplication([
            ('/api/v1/game/invite', CreateInviteHandler),
            ('/api/v1/game/pending', RetrieveInviteHandler),
            ('/api/v1/game/cancel', CancelInviteHandler)
        ])
        self.testapp = webtest.TestApp(app)
        self.user_one = User(username='Tester01', email='Tester01@email.com')
        self.user_two = User(username='Tester02', email='Tester02@email.com')
        self.user_one.put()
        self.user_two.put()
        self.jwt_token_player_one = token.encode_jwt({"userKey": self.user_one.key.urlsafe()})
        self.jwt_token_player_two = token.encode_jwt({"userKey": self.user_two.key.urlsafe()})

    def tearDown(self):
        super(TestCaseInvites, self).tearDown()

    def test_send_invites(self):
        # create the invite
        resp = self.testapp.post('/api/v1/game/invite',
                                 params=json.dumps({
                                     "jwt_token": self.jwt_token_player_one,
                                     "player_two_key": self.user_two.key.urlsafe()
                                 }),
                                 content_type='application/json')
        # verify the invite was sent to user_two
        resp = self.testapp.post('/api/v1/game/pending',
                                 params=json.dumps({
                                     "jwt_token": self.jwt_token_player_two
                                 }),
                                 content_type='application/json')
        data = json.loads(resp.body)
        self.assertEqual(len(data), 1, 'One invite was not created')

    def test_cancel_invites(self):
        # cancel an invite please, but first we need to have one
        invite = Invite(to_player=self.user_one.key,
                        to_player_name=self.user_one.username,
                        from_player=self.user_two.key,
                        from_player_name=self.user_two.username).put()
        resp = self.testapp.post('/api/v1/game/cancel',
                                 params=json.dumps({
                                     "jwt_token": self.jwt_token_player_two,
                                     "target_user": self.user_one.key.urlsafe()
                                 }),
                                 content_type='application/json')
        invite = invite.get()
        self.assertIn('200', str(resp))
        self.assertTrue(invite.rejected, 'The invite was not rejected')
