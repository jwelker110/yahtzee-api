import json

from helpers import request
from google.appengine.ext.ndb import Key

from models import Client


class CredentialsEP(request.RequestHandler):
    def post(self):
        """
        This will store the provided credentials in the datastore for future use. This
        allows the user to authenticate their users through our server so we can provide
        a JWT with the user claim
        :return: key - url safe string associated with these credentials
        """
        self.response.headers.add('Access-Control-Allow-Origin', '*')
        self.response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        data = json.loads(self.request.body)
        client_id = data.get('client_id')
        client_secret = data.get('client_secret')

        if client_id.replace(' ', '') == '' or client_secret.replace(' ', '') == '':
            return self.error(400)

        # check to make sure we don't already have an entry for this client id
        try:
            creds = Key("Client", client_id + client_secret).get()
        except Exception as e:
            print e.message
            creds = None

        if creds is None:
            # create the new client
            creds = Client(
                client_id=client_id,
                client_secret=client_secret
            )
            creds.key = Key("Client", client_id + client_secret)
            creds.put()

        # the urlsafe key can be used later to auth their user
        return self.response.write(json.dumps({"apiKey": creds.key.urlsafe()}))
