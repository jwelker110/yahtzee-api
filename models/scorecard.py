from google.appengine.ext import ndb


class Scorecard(ndb.Model):
    player = ndb.KeyProperty(kind='User', required=True)

    ones = ndb.IntegerProperty(default=-1)
    twos = ndb.IntegerProperty(default=-1)
    threes = ndb.IntegerProperty(default=-1)
    fours = ndb.IntegerProperty(default=-1)
    fives = ndb.IntegerProperty(default=-1)
    sixes = ndb.IntegerProperty(default=-1)

    upperSubTotal = ndb.IntegerProperty(default=0)
    bonus = ndb.ComputedProperty(lambda self: 35 if self.upperTotal >= 63 else 0)
    upperTotal = ndb.ComputedProperty(lambda self: self.bonus + self.upperTotal)

    threeOfKind = ndb.IntegerProperty(default=-1)
    fourOfKind = ndb.IntegerProperty(default=-1)
    fullHouse = ndb.IntegerProperty(default=-1)
    smStraight = ndb.IntegerProperty(default=-1)
    lgStraight = ndb.IntegerProperty(default=-1)
    yahtzee = ndb.IntegerProperty(default=-1)
    chance = ndb.IntegerProperty(default=-1)

    bonusYahtzee = ndb.IntegerProperty(repeated=True)

    lowerTotal = ndb.IntegerProperty(default=0)

    scoreTotal = ndb.ComputedProperty(lambda self: self.upperTotal + self.lowerTotal)
