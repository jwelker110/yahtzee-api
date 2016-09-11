from google.appengine.ext import ndb


class Turn(ndb.Model):
    roll_one = ndb.IntegerProperty(repeated=True)
    roll_two = ndb.IntegerProperty(repeated=True)
    roll_three = ndb.IntegerProperty(repeated=True)

    allocated_to = ndb.StringProperty(default=None)

    date_completed = ndb.DateTimeProperty(auto_now_add=True)
