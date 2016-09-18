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

from ep import CompleteTurnHandler, NewTurnHandler, TakeTurnHandler, \
    CreateInviteHandler, RetrieveInviteHandler, CancelInviteHandler, \
    UserAllHandler, UserGamesHandler, UserRollHistoryHandler, UserGamesHistoryHandler, \
    ViewGameHandler, UserRankHandler, HighScoreHandler, CancelGameHandler, ReauthHandler, \
    UserHandler


app = webapp2.WSGIApplication([
    ('/api/v1/turn/complete', CompleteTurnHandler),
    ('/api/v1/turn/new', NewTurnHandler),
    ('/api/v1/turn/take', TakeTurnHandler),
    ('/api/v1/invite/create', CreateInviteHandler),
    ('/api/v1/invite/retrieve', RetrieveInviteHandler),
    ('/api/v1/invite/cancel', CancelInviteHandler),
    ('/api/v1/game/view', ViewGameHandler),
    ('/api/v1/game/current', UserGamesHandler),
    ('/api/v1/game/forfeit', CancelGameHandler),
    ('/api/v1/game/rolls', UserRollHistoryHandler),
    ('/api/v1/game/history', UserGamesHistoryHandler),
    ('/api/v1/auth/reauth', ReauthHandler),
    ('/api/v1/auth/user', UserHandler),
    ('/api/v1/user/all', UserAllHandler),
    ('/api/v1/user/rank', UserRankHandler),
    ('/api/v1/user/highscore', HighScoreHandler),
])
