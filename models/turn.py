from google.appengine.ext import ndb


class Turn(ndb.Model):
    # the player this turn is associated with
    owner = ndb.StringProperty(required=True)
    # array of dice that get stored for the turn
    dice = ndb.IntegerProperty(repeated=True)
    # what part of the scorecard does this count towards?
    allocated_to = ndb.StringProperty(required=True)

    date_rolled = ndb.DateTimeProperty(auto_now_add=True)
