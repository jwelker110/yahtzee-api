import webtest
import json
import endpoints

from ep import CreateInviteHandler, RetrieveInviteHandler, CancelInviteHandler
from base import GameTestCase
from models import User, Invite
from helpers import token


class TestCaseInvites(GameTestCase):

    def setUp(self):
        super(TestCaseInvites, self).setUp()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        app = endpoints.api_server([
            CreateInviteHandler,
            RetrieveInviteHandler,
            CancelInviteHandler
        ], restricted=False)
        self.testapp = webtest.TestApp(app)
        self.user_one = User(username='Tester01', email='Tester01@email.com')
        self.user_two = User(username='Tester02', email='Tester02@email.com')
        self.user_one.put()
        self.user_two.put()
        self.jwt_token_player_one = token.encode_jwt({"user_key": self.user_one.key.urlsafe()})
        self.jwt_token_player_two = token.encode_jwt({"user_key": self.user_two.key.urlsafe()})

    def tearDown(self):
        super(TestCaseInvites, self).tearDown()

    def test_send_invites(self):
        # create the invite
        resp = self.testapp.post_json('/_ah/spi/CreateInviteHandler.create_invite', {
            "jwt_token": self.jwt_token_player_one,
            "player_two_key": self.user_two.key.urlsafe()
        })
        # verify the invite was sent to user_two
        resp = self.testapp.post_json('/_ah/spi/RetrieveInviteHandler.retrieve_invite', {
            "jwt_token": self.jwt_token_player_two
        })

        data = json.loads(resp.body)
        self.assertEqual(len(data['invites']), 1, 'One invite was not created')
        invite = Invite.query(Invite.from_player == self.user_one.key,
                              Invite.to_player == self.user_two.key).get()
        self.assertIsNotNone(invite)

    def test_send_invite_no_auth(self):
        # try to create the invite without auth
        resp = self.testapp.post('/_ah/spi/CreateInviteHandler.create_invite', expect_errors=True)
        self.assertIn('400', str(resp))

    def test_send_invite_already_exists(self):
        # try to send an invite to a user that already has an invite pending please
        # start by creating the invite
        invite = Invite(
            to_player=self.user_one.key,
            to_player_name=self.user_one.username,
            from_player=self.user_two.key,
            from_player_name=self.user_two.username
        )
        invite.put()

        # invite created, so let's have user_two try to send an invite to user_one
        resp = self.testapp.post('/_ah/spi/CreateInviteHandler.create_invite',
                                 params=json.dumps({
                                     "jwt_token": self.jwt_token_player_two,
                                     "player_two_key": self.user_one.key.urlsafe()}),
                                 content_type='application/json',
                                 expect_errors=True)
        self.assertIn('400', str(resp))

    def test_send_invite_wrong_args(self):
        # try to create an invite with the wrong arguments 'n stuff!
        resp = self.testapp.post('/_ah/spi/CreateInviteHandler.create_invite',
                                 params=json.dumps({
                                     "jwt_token": self.jwt_token_player_two,
                                     "wrong_args_please": self.user_one.key.urlsafe()}),
                                 content_type='application/json',
                                 expect_errors=True)
        self.assertIn('400', str(resp))

    def test_cancel_invites(self):
        # cancel an invite please, but first we need to have one
        invite = Invite(to_player=self.user_one.key,
                        to_player_name=self.user_one.username,
                        from_player=self.user_two.key,
                        from_player_name=self.user_two.username).put()
        resp = self.testapp.post('/_ah/spi/CancelInviteHandler.cancel_invite',
                                 params=json.dumps({
                                     "jwt_token": self.jwt_token_player_two,
                                     "target_user": self.user_one.key.urlsafe()
                                 }),
                                 content_type='application/json')
        invite = invite.get()
        self.assertIn('200', str(resp))
        self.assertTrue(invite.rejected, 'The invite was not rejected')

    def test_cancel_invite_not_exist(self):
        # try to cancel an invite that doesn't belong to the user
        user_three = User(username='Tester03', email='Tester03@email.com')
        user_three.put()
        user_three_jwt = token.encode_jwt({"user_key": user_three.key.urlsafe()})

        invite = Invite(
            to_player=self.user_one.key,
            to_player_name=self.user_one.username,
            from_player=self.user_two.key,
            from_player_name=self.user_two.username
        ).put()
        resp = self.testapp.post('/_ah/spi/CancelInviteHandler.cancel_invite',
                                 params=json.dumps({
                                     "jwt_token": user_three_jwt,
                                     "target_user": self.user_one.key.urlsafe()
                                 }),
                                 content_type='application/json',
                                 expect_errors=True)
        self.assertIn('400', str(resp))

    def test_cancel_invite_wrong_args(self):
        # send a cancel request with wrong args!
        resp = self.testapp.post_json('/_ah/spi/CancelInviteHandler.cancel_invite', {
            "jwt_token": self.jwt_token_player_one,
            "wrong_args_please": self.user_two.key.urlsafe()
        }, expect_errors=True)
        self.assertIn('400', resp.status)

    def test_retrieve_invite(self):
        # let's create two invites first
        user_three = User(
            username='Tester03',
            email='Tester03@email.com'
        )
        user_three.put()

        invite_one = Invite(
            to_player=self.user_one.key,
            to_player_name=self.user_one.username,
            from_player=self.user_two.key,
            from_player_name=self.user_two.username
        )
        invite_two = Invite(
            to_player=self.user_one.key,
            to_player_name=self.user_one.username,
            from_player=user_three.key,
            from_player_name=user_three.username
        )

        invite_one.put()
        invite_two.put()

        # created. Let's retrieve the invites
        resp = self.testapp.post('/_ah/spi/RetrieveInviteHandler.retrieve_invite',
                                 params=json.dumps({
                                     "jwt_token": self.jwt_token_player_one
                                 }),
                                 content_type='application/json')
        resp = json.loads(resp.body)
        self.assertEqual(len(resp['invites']), 2, 'Two invites were not retrieved after being created')

    def test_retrieve_rejected(self):
        # let's create two invites first
        user_three = User(
            username='Tester03',
            email='Tester03@email.com'
        )
        user_three.put()

        invite_one = Invite(
            to_player=self.user_one.key,
            to_player_name=self.user_one.username,
            from_player=self.user_two.key,
            from_player_name=self.user_two.username
        )
        invite_two = Invite(
            to_player=self.user_one.key,
            to_player_name=self.user_one.username,
            from_player=user_three.key,
            from_player_name=user_three.username,
            rejected=True
        )

        invite_one.put()
        invite_two.put()

        # created. Let's retrieve the invites
        resp = self.testapp.post('/_ah/spi/RetrieveInviteHandler.retrieve_invite',
                                 params=json.dumps({
                                     "jwt_token": self.jwt_token_player_one
                                 }),
                                 content_type='application/json')
        self.assertEqual(len(json.loads(resp.body)), 1,
                         'One invite was not retrieved after creating two and cancelling one')

    def test_accept_invite(self):
        # let's create invite first
        invite_one = Invite(
            to_player=self.user_one.key,
            to_player_name=self.user_one.username,
            from_player=self.user_two.key,
            from_player_name=self.user_two.username
        )

        invite_one.put()

        resp = self.testapp.post_json('/_ah/spi/CreateInviteHandler.create_invite', {
            "jwt_token": self.jwt_token_player_one,
            "player_two_key": self.user_two.key.urlsafe()
        })
        self.assertIn('200', resp.status)
