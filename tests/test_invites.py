import webapp2
import webtest

from ep import CreateInviteHandler
from base import GameTestCase


class TestCaseInvites(GameTestCase):
    jwt_token_player_one = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE0NzM4ODE1NDAsImlhdCI6MTQ3MzYyMjM0MCwidXNlcktleSI6ImFoSmtaWFotZVdGb2RIcGxaUzB4TkRJeE1EbHlIZ3NTQkZWelpYSWlGR3AzWld4clpYSXhNVEJBWjIxaGFXd3VZMjl0REEifQ.xEZ7kWXf7vyIqLrR5w95_gCIAw07xgVggTu--CryPms"
    jwt_token_player_two = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE0NzM4ODE1ODYsInVzZXJLZXkiOiJhaEprWlhaLWVXRm9kSHBsWlMweE5ESXhNRGx5SUFzU0JGVnpaWElpRm1scGMyRjBiM0pwZUdKdmVFQm5iV0ZwYkM1amIyME0iLCJpYXQiOjE0NzM2MjIzODZ9.9ybTAPntQyFRlqalmHNHko-bi5dr47xnnjHvigWNGoo"

    def setUp(self):
        super(TestCaseInvites, self).setUp()
        app = webapp2.WSGIApplication([
            ('/api/v1/user/game/invite', CreateInviteHandler)
        ])
        self.testapp = webtest.TestApp(app)

    def tearDown(self):
        super(TestCaseInvites, self).tearDown()

    def test_send_invites(self):
        # self.testapp.post('/api/v1/user/game/invite', params=json.dumps({'jwt_token': }))
        self.assertEqual(1, 1, '1 equals 1')
