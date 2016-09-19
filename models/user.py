from google.appengine.ext import ndb


class User(ndb.Model):
    username = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)

    wins = ndb.IntegerProperty(default=0)
    last_active = ndb.DateTimeProperty(auto_now_add=True)
