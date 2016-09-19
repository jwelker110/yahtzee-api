from protorpc import messages


class CancelGameRequestForm(messages.Message):
    jwt_token = messages.StringField(1, required=True)
    game_key = messages.StringField(2, required=True)


class UserGamesHistoryRequestForm(messages.Message):
    jwt_token = messages.StringField(1, required=True)
    offset = messages.IntegerField(2, default=0)


class GamesHistory(messages.Message):
    player_one = messages.StringField(1)
    player_two = messages.StringField(2)
    game_key = messages.StringField(3)


class UserGamesHistory(messages.Message):
    games = messages.MessageField(GamesHistory, 1, repeated=True)


class UserGamesHistoryResponseForm(messages.Message):
    games = messages.MessageField(UserGamesHistory, 1, repeated=True)


class UserRollHistoryRequestForm(messages.Message):
    jwt_token = messages.StringField(1, required=True)
    game_key = messages.StringField(2, required=True)


class UserRollHistory(messages.Message):
    roll_one = messages.IntegerField(1, repeated=True)
    roll_two = messages.IntegerField(2, repeated=True)
    roll_three = messages.IntegerField(3, repeated=True)
    allocated_to = messages.StringField(4)
    date_completed = messages.StringField(5)


class UserRollHistoryResponseForm(messages.Message):
    rolls = messages.MessageField(UserRollHistory, 1, repeated=True)


class CreateInviteRequestForm(messages.Message):
    jwt_token = messages.StringField(1, required=True)
    player_two_key = messages.StringField(2, required=True)


class Game(messages.Message):
    player_one = messages.StringField(1)
    player_one_name = messages.StringField(2)
    player_two = messages.StringField(3)
    player_two_name = messages.StringField(4)

    date_created = messages.StringField(5)

    # PLAYER ONE
    player_one_cancelled = messages.BooleanField(6)
    player_one_completed = messages.BooleanField(7)

    player_one_last_turn_date = messages.StringField(8)
    player_one_ones = messages.IntegerField(9)
    player_one_twos = messages.IntegerField(10)
    player_one_threes = messages.IntegerField(11)
    player_one_fours = messages.IntegerField(12)
    player_one_fives = messages.IntegerField(13)
    player_one_sixes = messages.IntegerField(14)

    player_one_upper_sub_total = messages.IntegerField(15)
    player_one_bonus = messages.IntegerField(16)
    player_one_upper_total = messages.IntegerField(17)

    player_one_three_of_a_kind = messages.IntegerField(18)
    player_one_four_of_a_kind = messages.IntegerField(19)
    player_one_full_house = messages.IntegerField(20)
    player_one_small_straight = messages.IntegerField(21)
    player_one_large_straight = messages.IntegerField(22)
    player_one_yahtzee = messages.IntegerField(23)
    player_one_chance = messages.IntegerField(24)

    player_one_bonus_yahtzee = messages.IntegerField(25)
    player_one_lower_total = messages.IntegerField(26)
    player_one_score_total = messages.IntegerField(27)

    # PLAYER TWO
    player_two_cancelled = messages.BooleanField(28)
    player_two_completed = messages.BooleanField(29)

    player_two_last_turn_date = messages.StringField(30)
    player_two_ones = messages.IntegerField(31)
    player_two_twos = messages.IntegerField(32)
    player_two_threes = messages.IntegerField(34)
    player_two_fours = messages.IntegerField(35)
    player_two_fives = messages.IntegerField(36)
    player_two_sixes = messages.IntegerField(37)

    player_two_upper_sub_total = messages.IntegerField(38)
    player_two_bonus = messages.IntegerField(39)
    player_two_upper_total = messages.IntegerField(40)

    player_two_three_of_a_kind = messages.IntegerField(41)
    player_two_four_of_a_kind = messages.IntegerField(42)
    player_two_full_house = messages.IntegerField(43)
    player_two_small_straight = messages.IntegerField(44)
    player_two_large_straight = messages.IntegerField(45)
    player_two_yahtzee = messages.IntegerField(46)
    player_two_chance = messages.IntegerField(47)

    player_two_bonus_yahtzee = messages.IntegerField(48)
    player_two_lower_total = messages.IntegerField(49)
    player_two_score_total = messages.IntegerField(50)

    game_completed = messages.BooleanField(51)
    winner_score = messages.IntegerField(52)
    winner_name = messages.IntegerField(53)


class CreateInviteResponseForm(messages.Message):
    game_key = messages.StringField(1)
    game = messages.MessageField(Game, 2)


class RetrieveInviteRequestForm(messages.Message):
    jwt_token = messages.StringField(1, required=True)
    offset = messages.IntegerField(2, default=0)


class Invite(messages.Message):
    inviter = messages.StringField(1)
    inviter_name = messages.StringField(2)


class RetrieveInviteResponseForm(messages.Message):
    invites = messages.MessageField(Invite, 1, repeated=True)


class CancelInviteRequestForm(messages.Message):
    jwt_token = messages.StringField(1, required=True)
    target_user = messages.StringField(2, required=True)


class TakeTurnRequestForm(messages.Message):
    jwt_token = messages.StringField(1, required=True)
    game_key = messages.StringField(2, required=True)
    turn_key = messages.StringField(3, required=True)
    dice_to_roll = messages.IntegerField(4, repeated=True)


class TakeTurnResponseForm(messages.Message):
    game_key = messages.StringField(1, required=True)
    turn_key = messages.StringField(2, required=True)
    roll_results = messages.IntegerField(3, repeated=True)
    turn_roll_count = messages.IntegerField(4)


class NewTurnRequestForm(messages.Message):
    jwt_token = messages.StringField(1, required=True)
    game_key = messages.StringField(2, required=True)


class NewTurnResponseForm(messages.Message):
    game_key = messages.StringField(1)
    turn_key = messages.StringField(2)
    roll_results = messages.IntegerField(3)
    turn_roll_count = messages.IntegerField(4)


class CompleteTurnRequestForm(messages.Message):
    jwt_token = messages.StringField(1, required=True)
    game_key = messages.StringField(2, required=True)
    allocate_to = messages.StringField(3, required=True)


class ViewGameRequestForm(messages.Message):
    jwt_token = messages.StringField(1, required=True)
    game_key = messages.StringField(2, required=True)


class ViewGameResponseForm(messages.Message):
    game_key = messages.StringField(1)
    game = messages.MessageField(Game, 2)
