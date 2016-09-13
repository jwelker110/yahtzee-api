import webapp2
import webtest
import json

from models import User
from base import GameTestCase
from ep import UserAllHandler


class TestCaseUsers(GameTestCase):

    def setUp(self):
        super(TestCaseUsers, self).setUp()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        app = webapp2.WSGIApplication([
            ('/api/v1/user/all', UserAllHandler)
        ])
        self.testapp = webtest.TestApp(app)

    def tearDown(self):
        super(TestCaseUsers, self).tearDown()

    def test_all_users_empty(self):
        resp = self.testapp.get('/api/v1/user/all')
        data = json.loads(resp.body)
        self.assertEqual(len(data), 0, 'Data has stuff in it!')

    def test_all_users(self):
        User(username='Tester01', email='Tester01@email.com').put()
        User(username='Tester02', email='Tester02@email.com').put()

        resp = self.testapp.get('/api/v1/user/all')
        data = json.loads(resp.body)
        self.assertEqual(len(data), 2, 'Data did not contain two user entities')

    def test_all_users_offset(self):
        User(username='Tester01', email='Tester01@email.com').put()
        User(username='Tester02', email='Tester02@email.com').put()

        resp = self.testapp.get('/api/v1/user/all?offset=1')
        data = json.loads(resp.body)
        self.assertEqual(len(data), 1, 'Data did not contain one user entity')
