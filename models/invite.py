from google.appengine.ext import ndb


class Invite(ndb.Model):
    from_player = ndb.KeyProperty(kind='User', required=True)
    from_player_name = ndb.StringProperty(required=True)
    to_player = ndb.KeyProperty(kind='User', required=True)
    to_player_name = ndb.StringProperty(required=True)

    accepted = ndb.BooleanProperty(default=False)
    rejected = ndb.BooleanProperty(default=False)
