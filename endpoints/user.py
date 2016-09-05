import httplib2
import json

from google.appengine.ext.ndb import Key
from apiclient import discovery
from oauth2client import client

from models import Client, User
from helpers import request


class UserEP(request.RequestHandler):
    def post(self):
        """
        Verifies the identity of the user via Oauth using the credentials key provided. If the user
        already exists, we return a JWT with their claim. If they don't already exist, we create their
        user in the datastore and return a JWT with their claim.
        :return: JWT with the user's claim, or nothing
        """
        self.response.headers.add('Access-Control-Allow-Origin', '*')
        self.response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        print self.request.body
        data = json.loads(self.request.body)
        # credentials key so we know which API to hit
        cred_key = data.get('credKey')
        # cred_key = self.request.get('key')
        auth_code = data.get('authCode')

        print cred_key
        print auth_code

        if cred_key.replace(' ', '') == '' or auth_code.replace(' ', '') == '':
            return self.error(400)

        try:
            creds = Key(urlsafe=cred_key).get()
        except Exception as e:
            print e.message
            creds = None

        if creds is None:
            return self.error(400)

        print creds
        # we have the credentials associated with this client so
        # let's go ahead and verify the user
        credentials = client.credentials_from_code(
            creds.client_id,
            creds.client_secret,
            'email',
            auth_code
        )

        # verifying the user
        http_auth = credentials.authorize(httplib2.Http())
        service = discovery.build('oauth2', 'v2', http=http_auth)
        userinfo = service.userinfo().get().execute()

        # todo ok now create the user and jwt and pass it back!
        print userinfo['email']

        # check whether the user exists any more or not



        return self.response.write(userinfo)
