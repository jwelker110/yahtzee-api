from google.appengine.ext import ndb


class Roll(ndb.Model):
    dice = ndb.IntegerProperty(repeated=True)

    date_rolled = ndb.DateTimeProperty(auto_now_add=True)
