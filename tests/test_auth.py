import webapp2
import webtest
import json
import time

from base import GameTestCase
from ep import ReauthHandler

from models import User
from helpers import token


class TestCaseAuth(GameTestCase):

    def setUp(self):
        super(TestCaseAuth, self).setUp()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        app = webapp2.WSGIApplication([
            ('/api/v1/user/reauth', ReauthHandler)
        ])
        self.testapp = webtest.TestApp(app)

        user_one = User(username='Tester01', email='Tester01@email.com').put()
        user_two = User(username='Tester02', email='Tester02@email.com').put()
        self.jwt_token_player_one = token.encode_jwt({"userKey": user_one.urlsafe()})
        self.jwt_token_player_two = token.encode_jwt({"userKey": user_two.urlsafe()})

    def tearDown(self):
        super(TestCaseAuth, self).tearDown()

    def test_user_reauth(self):
        resp = self.testapp.post('/api/v1/user/reauth',
                                 params=json.dumps({"jwt_token": self.jwt_token_player_one}),
                                 content_type='application/json')
        data = json.loads(resp.body)
        self.assertIn('jwt_token', data, 'JWT was not returned for player one')

    def test_user_no_auth(self):
        resp = self.testapp.post('/api/v1/user/reauth', expect_errors=True)
        self.assertIn('400', str(resp))
