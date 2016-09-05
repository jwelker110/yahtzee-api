from google.appengine.ext import ndb


class Game(ndb.Model):
    player_one = ndb.KeyProperty(kind='User', required=True)
    player_two = ndb.KeyProperty(kind='User', required=True)

    turn_count = ndb.IntegerProperty(default=0)

    last_turn_date = ndb.DateTimeProperty(auto_now_add=True)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
