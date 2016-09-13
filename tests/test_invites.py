import webapp2
import webtest
import json

from ep import CreateInviteHandler, RetrieveInviteHandler
from base import GameTestCase
from models import User
from helpers import token


class TestCaseInvites(GameTestCase):

    def setUp(self):
        super(TestCaseInvites, self).setUp()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        app = webapp2.WSGIApplication([
            ('/api/v1/user/game/invite', CreateInviteHandler),
            ('/api/v1/user/game/pending', RetrieveInviteHandler)
        ])
        self.testapp = webtest.TestApp(app)

    def tearDown(self):
        super(TestCaseInvites, self).tearDown()

    def test_send_invites(self):
        user_one = User(username='Tester01', email='Tester01@email.com')
        user_two = User(username='Tester02', email='Tester02@email.com')

        user_one.put()
        user_two.put()

        jwt_one = token.encode_jwt({"userKey": user_one.key.urlsafe()})
        jwt_two = token.encode_jwt({"userKey": user_two.key.urlsafe()})

        # create the invite
        resp = self.testapp.post('/api/v1/user/game/invite',
                                 params=json.dumps({
                                     "jwt_token": jwt_one,
                                     "player_two_key": user_two.key.urlsafe()
                                 }),
                                 content_type='application/json')
        # verify the invite was sent to user_two
        resp = self.testapp.post('/api/v1/user/game/pending',
                                 params=json.dumps({
                                     "jwt_token": jwt_two
                                 }),
                                 content_type='application/json')
        data = json.loads(resp.body)
        print data
        self.assertEqual(len(data), 1, 'One invite was not created')
