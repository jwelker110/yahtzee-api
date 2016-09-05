from google.appengine.ext import ndb


class Client(ndb.Model):
    # used for accessing Google API on behalf of the requesting app
    client_id = ndb.StringProperty(required=True)
    client_secret = ndb.StringProperty(required=True)
