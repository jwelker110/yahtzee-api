# import webtest
# import json
# import random
# import endpoints
#
# from models import Game
# from models import User
# from base import GameTestCase
# from ep import UserAllHandler, HighScoreHandler, UserRankHandler
#
# TODO not sure why, but having some trouble testing 'GET' endpoints
#
# class TestCaseUsers(GameTestCase):
#
#     def setUp(self):
#         super(TestCaseUsers, self).setUp()
#         self.testbed.init_datastore_v3_stub()
#         self.testbed.init_memcache_stub()
#         app = endpoints.api_server([
#             UserAllHandler,
#             HighScoreHandler,
#             UserRankHandler
#         ], restricted=False)
#         self.testapp = webtest.TestApp(app)
#
#     def tearDown(self):
#         super(TestCaseUsers, self).tearDown()
#
#     def test_all_users_empty(self):
#         resp = self.testapp.get('/_ah/api/user/all')
#         data = json.loads(resp.body)
#         self.assertEqual(len(data), 0, 'Data has stuff in it!')
#
#     def test_all_users(self):
#         User(username='Tester01', email='Tester01@email.com').put()
#         User(username='Tester02', email='Tester02@email.com').put()
#
#         resp = self.testapp.get('/_ah/spi/UserAllHandler.retrieve_users')
#         data = json.loads(resp.body)
#         self.assertEqual(len(data), 2, 'Data did not contain two user entities')
#
#     def test_all_users_offset(self):
#         User(username='Tester01', email='Tester01@email.com').put()
#         User(username='Tester02', email='Tester02@email.com').put()
#
#         resp = self.testapp.get('/_ah/spi/UserAllHandler.retrieve_users')
#         data = json.loads(resp.body)
#         self.assertEqual(len(data), 1, 'Data did not contain one user entity')
#
#     def test_user_ranking(self):
#         """
#         Test to ensure that user rank is retrieved, based on most wins
#         """
#         for _ in xrange(0, 15):
#             User(username='Tester %s' % _, email='Tester@email.com', wins=random.randint(0, 10)).put()
#
#         resp = self.testapp.get('/_ah/spi/UserRankHandler.user_rank')
#         resp = json.loads(resp.body)
#         self.assertEqual(len(resp), 10, 'test')
#
#     def test_user_high_score(self):
#         """
#         Test to ensure that user rank is retrieved, based on most wins
#         """
#         users = []
#         for _ in xrange(0, 10):
#             users.append(User(username='Tester %s' % (_ + 1), email='Tester@email.com', wins=random.randint(0, 10)).put())
#
#         for _ in xrange(0, 5):
#             user_one = users[_].get()
#             user_two = users[9 - _].get()
#             game = Game(player_one=user_one.key,
#                          player_one_name=user_one.username,
#                          player_two=user_two.key,
#                          player_two_name=user_two.username,
#                          player_one_upper_sub_total=random.randint(10, 80),
#                          player_one_lower_total=random.randint(30, 150),
#                          player_two_upper_sub_total=random.randint(10, 80),
#                          player_two_lower_total=random.randint(30, 150),
#                          player_one_completed=True,
#                          player_two_completed=True)
#             game.put()
#             # if you'd like to see the scores
#             # print "player one score: %s" % game.player_one_score_total
#             # print "player two score: %s" % game.player_two_score_total
#             # print "++++++++++++++++++++++++++"
#         resp = self.testapp.get('/_ah/spi/HighScoreHandler.user_score')
#         resp = json.loads(resp.body)
#         self.assertEqual(len(resp), 5, '5 scores were not returned')
