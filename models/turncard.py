import roll

from google.appengine.ext import ndb


class TurnCard(ndb.Model):
    # the player this turn is associated with
    owner = ndb.KeyProperty(kind='User', required=True)
    game = ndb.KeyProperty(kind='Game', required=True)

    roll_one = ndb.StructuredProperty()