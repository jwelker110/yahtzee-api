from google.appengine.ext import ndb


class DateTimeProperty(ndb.DateTimeProperty):
    """
    Thank you Max http://stackoverflow.com/questions/25871308/appengine-datastore-to-dict-alternative-to-serialize-ndb-model-to-json
    """
    def _db_set_value(self, v, p, value):
        super(DateTimeProperty, self)._db_set_value(v, p, value)

    def _get_for_dict(self, entity):
        val = super(DateTimeProperty, self)._get_for_dict(entity)
        return val.isoformat()


class Game(ndb.Model):
    player_one = ndb.KeyProperty(kind='User', required=True)
    player_one_name = ndb.StringProperty(required=True)
    player_two = ndb.KeyProperty(kind='User', required=True)
    player_two_name = ndb.StringProperty(required=True)

    date_created = DateTimeProperty(auto_now_add=True)

    # PLAYER ONE
    player_one_cancelled = ndb.BooleanProperty(default=False)
    player_one_completed = ndb.BooleanProperty(default=False)

    player_one_last_turn_date = DateTimeProperty(auto_now_add=True)
    player_one_ones = ndb.IntegerProperty(default=None)
    player_one_twos = ndb.IntegerProperty(default=None)
    player_one_threes = ndb.IntegerProperty(default=None)
    player_one_fours = ndb.IntegerProperty(default=None)
    player_one_fives = ndb.IntegerProperty(default=None)
    player_one_sixes = ndb.IntegerProperty(default=None)

    player_one_upper_sub_total = ndb.IntegerProperty(default=0)
    player_one_bonus = ndb.ComputedProperty(lambda self: 35 if self.player_one_upper_sub_total >= 63 else 0)
    player_one_upper_total = ndb.ComputedProperty(lambda self: self.player_one_bonus + self.player_one_upper_sub_total)

    player_one_three_of_a_kind = ndb.IntegerProperty(default=None)
    player_one_four_of_a_kind = ndb.IntegerProperty(default=None)
    player_one_full_house = ndb.IntegerProperty(default=None)
    player_one_small_straight = ndb.IntegerProperty(default=None)
    player_one_large_straight = ndb.IntegerProperty(default=None)
    player_one_yahtzee = ndb.IntegerProperty(default=None)
    player_one_chance = ndb.IntegerProperty(default=None)

    player_one_bonus_yahtzee = ndb.IntegerProperty(repeated=True)

    player_one_lower_total = ndb.IntegerProperty(default=0)

    player_one_score_total = ndb.ComputedProperty(lambda self: self.player_one_upper_total +
                                                               self.player_one_lower_total +
                                                               len(self.player_one_bonus_yahtzee) * 50)

    # PLAYER TWO
    player_two_cancelled = ndb.BooleanProperty(default=False)
    player_two_completed = ndb.BooleanProperty(default=False)

    player_two_last_turn_date = DateTimeProperty(auto_now_add=True)
    player_two_ones = ndb.IntegerProperty(default=None)
    player_two_twos = ndb.IntegerProperty(default=None)
    player_two_threes = ndb.IntegerProperty(default=None)
    player_two_fours = ndb.IntegerProperty(default=None)
    player_two_fives = ndb.IntegerProperty(default=None)
    player_two_sixes = ndb.IntegerProperty(default=None)

    player_two_upper_sub_total = ndb.IntegerProperty(default=0)
    player_two_bonus = ndb.ComputedProperty(lambda self: 35 if self.player_two_upper_sub_total >= 63 else 0)
    player_two_upper_total = ndb.ComputedProperty(lambda self: self.player_two_bonus + self.player_two_upper_sub_total)

    player_two_three_of_a_kind = ndb.IntegerProperty(default=None)
    player_two_four_of_a_kind = ndb.IntegerProperty(default=None)
    player_two_full_house = ndb.IntegerProperty(default=None)
    player_two_small_straight = ndb.IntegerProperty(default=None)
    player_two_large_straight = ndb.IntegerProperty(default=None)
    player_two_yahtzee = ndb.IntegerProperty(default=None)
    player_two_chance = ndb.IntegerProperty(default=None)

    player_two_bonus_yahtzee = ndb.IntegerProperty(repeated=True)

    player_two_lower_total = ndb.IntegerProperty(default=0)

    player_two_score_total = ndb.ComputedProperty(lambda self: self.player_two_upper_total +
                                                               self.player_two_lower_total +
                                                               len(self.player_two_bonus_yahtzee) * 50)

    game_completed = ndb.ComputedProperty(lambda self: self.player_one_completed and self.player_two_completed)

    def _winner_score(self):
        if self.player_two_cancelled:
            return self.player_one_score_total
        elif self.player_one_cancelled:
            return self.player_two_score_total
        elif self.player_one_score_total > self.player_two_score_total:
            return self.player_one_score_total
        return self.player_two_score_total

    winner_score = ndb.ComputedProperty(_winner_score)

    def _winner_name(self):
        if self.player_two_cancelled:
            return self.player_one_name
        elif self.player_one_cancelled:
            return self.player_two_name
        elif self.player_one_score_total > self.player_two_score_total:
            return self.player_one_name
        elif self.player_one_score_total == self.player_two_score_total:
            return '%s, %s' % (self.player_one_name, self.player_two_name)
        return self.player_two_name

    winner_name = ndb.ComputedProperty(_winner_name)
