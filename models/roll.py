from google.appengine.ext import ndb


class Roll(ndb.Model):
    dice = ndb.IntegerProperty(default=None)

    date_rolled = ndb.DateTimeProperty(auto_now_add=True)
