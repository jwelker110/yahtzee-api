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
import datetime

from google.appengine.api import mail, app_identity
from models import User


class ReminderHandler(webapp2.RequestHandler):
    def options(self):
        self.response.headers.add_header('Access-Control-Allow-Origin', 'http://google.com')

    def get(self):
        """Send a reminder email to each User that has been inactive for 3 days but not more than 4
        Called every 3 days (72 hours) using a cron job"""
        app_id = app_identity.get_application_id()
        users = User.query(User.last_active < datetime.datetime.utcnow() - datetime.timedelta(0),
                           User.last_active > datetime.datetime.utcnow() - datetime.timedelta(1)).fetch()
        for user in users:
            print 'emailing...'
            subject = 'Yahtzee!'
            body = 'Hello {}, we haven\'t seen you in a while!'.format(user.username)
            # This will send test emails, the arguments to send_mail are:
            # from, to, subject, body
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)

app = webapp2.WSGIApplication([
    ('/tasks/reminder', ReminderHandler)
])
