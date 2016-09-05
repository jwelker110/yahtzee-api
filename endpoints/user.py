import httplib2
import json
import os
import string

from google.appengine.ext.ndb import Key
from apiclient import discovery
from oauth2client import client

from models import Client, User
from helpers import request, token


class UserEP(request.RequestHandler):
    def post(self):
        """
        Verifies the identity of the user via Oauth using the credentials key provided and the user's auth code. If the
        user already exists, we return a JWT with their claim. If they don't already exist, we create their
        user in the datastore and return a JWT with their claim.
        :return: JWT with the user's claim, or nothing
        """
        self.response.headers.add('Access-Control-Allow-Origin', '*')
        self.response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        data = json.loads(self.request.body)
        # credentials key so we know which API to hit
        cred_key = data.get('credKey')
        # code associated with the user so we can verify their identity
        auth_code = data.get('authCode')

        # make sure we actually have the keys
        if cred_key.replace(' ', '') == '' or auth_code.replace(' ', '') == '':
            return self.error(400)

        # get the API credentials associated with the app that is
        # accessing out endpoints
        creds = Key(urlsafe=cred_key).get()

        if creds is None:
            return self.error(400)

        # we have the credentials associated with this client so
        # let's go ahead and verify the user using OAuth
        credentials = client.credentials_from_code(
            creds.client_id,
            creds.client_secret,
            'email',
            auth_code
        )

        # verifying the user
        try:
            http_auth = credentials.authorize(httplib2.Http())
            service = discovery.build('oauth2', 'v2', http=http_auth)
            userinfo = service.userinfo().get().execute()  # we should have the userinfo
        except:
            # were we given the wrong user info?
            return self.error(400)

        print userinfo
        # ok now create the user and jwt and pass it back!
        email = userinfo.get('email')

        if email is None:
            return self.error(400)

        # check whether the user exists
        user = User.get_by_id(email)

        if user is None:
            try:
                token_salt = os.urandom(64).encode('base-64')
                # create the user
                username = email.split('@')[0]
                user = User(
                    username=username,
                    email=email,
                    token_salt=token_salt
                )
                user.key = Key('User', email)
                user.put()
            except Exception as e:
                print e.message
                return self.error(500)

        payload = {
            "userKey": user.key.urlsafe()
        }
        jwt = token.encode_jwt(payload, os.environ.get('JWT_KEY'))
        return self.response.write(jwt)
