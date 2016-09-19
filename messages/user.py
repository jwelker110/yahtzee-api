from protorpc import messages


class UserGamesRequestForm(messages.Message):
    jwt_token = messages.StringField(1, required=True)
    offset = messages.IntegerField(2, default=0)


class UserGames(messages.Message):
    player_one = messages.StringField(1)
    player_two = messages.StringField(2)
    game_key = messages.StringField(3)


class UserGamesResponseForm(messages.Message):
    games = messages.MessageField(UserGames, 1, repeated=True)


class UserRank(messages.Message):
    username = messages.StringField(1)
    wins = messages.IntegerField(2)


class UserRankResponseForm(messages.Message):
    players = messages.MessageField(UserRank, 1, repeated=True)


class UserHighScore(messages.Message):
    username = messages.StringField(1)
    score = messages.IntegerField(2)


class UserHighScoreResponseForm(messages.Message):
    players = messages.MessageField(UserHighScore, 1, repeated=True)


class UserAllRequestForm(messages.Message):
    offset = messages.IntegerField(1, default=0)


class UserForm(messages.Message):
    username = messages.StringField(1)
    user_key = messages.StringField(2)


class UserAllResponseForm(messages.Message):
    users = messages.MessageField(UserForm, 1, repeated=True)
