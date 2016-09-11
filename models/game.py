from google.appengine.ext import ndb


class Game(ndb.Model):
    player_one = ndb.KeyProperty(kind='User', required=True)
    player_two = ndb.KeyProperty(kind='User', required=True)

    date_created = ndb.DateTimeProperty(auto_now_add=True)

    cancelled = ndb.BooleanProperty(default=False)
    completed = ndb.BooleanProperty(default=False)

    # PLAYER ONE
    player_one_ones = ndb.IntegerProperty(default=None)
    player_one_twos = ndb.IntegerProperty(default=None)
    player_one_threes = ndb.IntegerProperty(default=None)
    player_one_fours = ndb.IntegerProperty(default=None)
    player_one_fives = ndb.IntegerProperty(default=None)
    player_one_sixes = ndb.IntegerProperty(default=None)

    player_one_upper_sub_total = ndb.IntegerProperty(default=0)
    player_one_bonus = ndb.ComputedProperty(lambda self: 35 if self.player_one_upper_total >= 63 else 0)
    player_one_upper_total = ndb.ComputedProperty(lambda self: self.player_one_bonus + self.player_one_upper_total)

    player_one_three_of_a_kind = ndb.IntegerProperty(default=None)
    player_one_four_of_a_kind = ndb.IntegerProperty(default=None)
    player_one_full_house = ndb.IntegerProperty(default=None)
    player_one_small_straight = ndb.IntegerProperty(default=None)
    player_one_large_straight = ndb.IntegerProperty(default=None)
    player_one_yahtzee = ndb.IntegerProperty(default=None)
    player_one_chance = ndb.IntegerProperty(default=None)

    player_one_bonus_yahtzee = ndb.IntegerProperty(repeated=True)

    player_one_lower_total = ndb.IntegerProperty(default=0)

    player_one_score_total = ndb.ComputedProperty(lambda self: self.player_one_upper_total + self.player_one_lower_total)

    # PLAYER TWO
    player_two_ones = ndb.IntegerProperty(default=None)
    player_two_twos = ndb.IntegerProperty(default=None)
    player_two_threes = ndb.IntegerProperty(default=None)
    player_two_fours = ndb.IntegerProperty(default=None)
    player_two_fives = ndb.IntegerProperty(default=None)
    player_two_sixes = ndb.IntegerProperty(default=None)

    player_two_upper_sub_total = ndb.IntegerProperty(default=0)
    player_two_bonus = ndb.ComputedProperty(lambda self: 35 if self.player_two_upper_total >= 63 else 0)
    player_two_upper_total = ndb.ComputedProperty(lambda self: self.player_two_bonus + self.upper_total)

    player_two_three_of_a_kind = ndb.IntegerProperty(default=None)
    player_two_four_of_a_kind = ndb.IntegerProperty(default=None)
    player_two_full_house = ndb.IntegerProperty(default=None)
    player_two_small_straight = ndb.IntegerProperty(default=None)
    player_two_large_straight = ndb.IntegerProperty(default=None)
    player_two_yahtzee = ndb.IntegerProperty(default=None)
    player_two_chance = ndb.IntegerProperty(default=None)

    player_two_bonus_yahtzee = ndb.IntegerProperty(repeated=True)

    player_two_lower_total = ndb.IntegerProperty(default=0)

    player_two_score_total = ndb.ComputedProperty(lambda self: self.player_two_upper_total + self.player_two_lower_total)
