import webapp2
import webtest
import json

from base import GameTestCase
from ep import ReauthHandler, UserAllHandler


class TestCaseAuth(GameTestCase):
    jwt_token_player_one = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE0NzM4ODE1NDAsImlhdCI6MTQ3MzYyMjM0MCwidXNlcktleSI6ImFoSmtaWFotZVdGb2RIcGxaUzB4TkRJeE1EbHlIZ3NTQkZWelpYSWlGR3AzWld4clpYSXhNVEJBWjIxaGFXd3VZMjl0REEifQ.xEZ7kWXf7vyIqLrR5w95_gCIAw07xgVggTu--CryPms"
    jwt_token_player_two = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE0NzM4ODE1ODYsInVzZXJLZXkiOiJhaEprWlhaLWVXRm9kSHBsWlMweE5ESXhNRGx5SUFzU0JGVnpaWElpRm1scGMyRjBiM0pwZUdKdmVFQm5iV0ZwYkM1amIyME0iLCJpYXQiOjE0NzM2MjIzODZ9.9ybTAPntQyFRlqalmHNHko-bi5dr47xnnjHvigWNGoo"

    def setUp(self):
        super(TestCaseAuth, self).setUp()
        app = webapp2.WSGIApplication([
            ('/api/v1/user/reauth', ReauthHandler),
            ('/api/v1/user/all', UserAllHandler)  # todo move this to separate module
        ])
        self.testapp = webtest.TestApp(app)

    def tearDown(self):
        super(TestCaseAuth, self).tearDown()

    def test_user_reauth(self):
        resp = self.testapp.post('/api/v1/user/reauth',
                                 params=json.dumps({"jwt_token": self.jwt_token_player_one}),
                                 content_type='application/json')
        data = json.loads(resp.body)

        self.assertIn('jwt_token', data, 'JWT was not returned for player one')
        self.assertNotEqual(self.jwt_token_player_one, data.get('jwt_token'))

    def test_all_users(self):
        # todo move to separate module
        resp = self.testapp.get('/api/v1/user/all')

        data = json.loads(resp.body)
        print data
        self.assertEqual(len(data), 0, 'Data has stuff in it!')
