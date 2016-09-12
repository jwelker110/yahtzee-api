#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

from ep import UserHandler, ReauthHandler
from ep import CreateInviteHandler
from ep import UserAllHandler, UserRankHandler


class PlaceholderEP(webapp2.RequestHandler):
    def get(self):
        return self.response.write('This is a test endpoint')

app = webapp2.WSGIApplication([
    ('/', PlaceholderEP),
    ('/api/v1/user/auth', UserHandler),
    ('/api/v1/user/reauth', ReauthHandler),
    ('/api/v1/game/invite', CreateInviteHandler),
    ('/api/v1/user/all', UserAllHandler),
    ('/api/v1/user/rank', UserRankHandler),
    # ('/api/v1/user/game/history.json', PlaceholderEP),
    # ('/api/v1/user/game/all.json', PlaceholderEP),
    # ('/api/v1/user/highscores.json', PlaceholderEP),
    # ('/api/v1/game/create.json', PlaceholderEP),
    # ('/api/v1/game/turn.json', PlaceholderEP),
    # ('/api/v1/game/roll.json', PlaceholderEP),
    # ('/api/v1/game/cancel', PlaceholderEP),
], debug=True)
