import sys
import unittest

from google.appengine.ext import testbed
from google.appengine.ext import ndb


class GameTestCase(unittest.TestCase):

    def setUp(self):
        # obtain the testbed
        self.testbed = testbed.Testbed()
        self.testbed.setup_env(current_version_id="1.0")
        # start the testbed
        self.testbed.setup_env(JWT_SECRET='The secret, secret key')
        self.testbed.activate()

        # clear anything stored to prevent data leak between tests
        ndb.get_context().clear_cache()

    def tearDown(self):
        # done with it until next test
        self.testbed.deactivate()
