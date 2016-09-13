from google.appengine.ext import ndb


class User(ndb.Model):
    username = ndb.StringProperty(required=True)
    username_lower = ndb.ComputedProperty(lambda self: self.username.lower())
    email = ndb.StringProperty(required=True)

    wins = ndb.IntegerProperty(default=0)
