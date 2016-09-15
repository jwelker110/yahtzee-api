import json

from helpers import request, decorators
from models import Game, Invite, TurnCard
from google.appengine.ext.ndb import Key


class CreateInviteHandler(request.RequestHandler):
    @decorators.jwt_required
    def post(self, payload):
        """
        So take the provided user's id and go ahead and start a game with their id and then
        the tentative player two's id as well. Verify JWT and that the user doesn't already
        have a game with player two before creating it.
        :return:
        """
        self.response.headers.add('Access-Control-Allow-Origin', '*')
        self.response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        self.response.headers['Content-Type'] = 'application/json'

        if self.request.body is None or self.request.body is '':
            return self.error(400)

        data = json.loads(self.request.body)
        player_two_key = data.get('player_two_key')

        if player_two_key is None or player_two_key is '':
            return self.response.set_status(400, '\'player_two_key\' argument was not included in the request')

        user = Key(urlsafe=payload.get('userKey')).get()

        if user is None:
            # not sure how the JWT slipped through but they aren't authorized to do this
            return self.error(401)

        # grab player two please
        player_two = Key(urlsafe=player_two_key).get()

        if player_two is None:
            return self.error(400)

        # awesome we have player one and two
        game = Game.query(
            Game.player_one == user.key,
            Game.player_two == player_two.key,
            Game.player_one_completed == False,
            Game.player_two_completed == False).get()

        if game is None:
            game = Game.query(Game.player_one == player_two.key,
                              Game.player_two == user.key,
                              Game.player_one_completed == False,
                              Game.player_two_completed == False).get()

        # if a game exists between these users, they need to finish it first please
        if game is not None:
            # not entirely certain what to set here, as the request wasn't necessarily wrong, but the
            # user already has a game with player_two
            return self.response.set_status(400, "An existing game must be finished before starting another one")

        # let's check for an existing invite between these players
        invite = Invite.query(
            Invite.from_player == user.key,
            Invite.to_player == player_two.key,
            Invite.accepted == False,
            Invite.rejected == False
        ).get()

        if invite is not None:
            return self.response.set_status(400, "A pending invite must be accepted or declined before creating another one")

        invite = Invite.query(
            Invite.from_player == player_two.key,
            Invite.to_player == user.key,
            Invite.accepted == False,
            Invite.rejected == False
        ).get()

        if invite is not None:
            # awesome! the inviter already has an invitation from the invitee.
            # start a game, and create the turncards for each player
            try:
                game = Game(
                    player_one=player_two.key,
                    player_two=user.key
                )
                player_one_turncard = TurnCard(
                    owner=player_two.key,
                    game=game.key
                )
                player_two_turncard = TurnCard(
                    owner=user.key,
                    game=game.key
                )
                player_one_turncard.put()
                player_two_turncard.put()
                game.put()

                return self.response.write(json.dumps({
                    "game_key": game.key.urlsafe(),
                    "game": game.to_dict()
                }))

            except:
                return self.response.set_status(500, 'An error occurred while attempting to create a game')

        # alright there are no invites between these players yet so let's make one
        try:
            invite = Invite(
                from_player=user.key,
                from_player_name=user.username,
                to_player=player_two.key,
                to_player_name=player_two.username
            )
            invite.put()
            return self.response.set_status(200)
        except:
            return self.response.set_status(500, 'An error occurred while attempting to create an invite')


class RetrieveInviteHandler(request.RequestHandler):
    @decorators.jwt_required
    def post(self, payload):
        """
        Retrieve the next 10 invites associated with the user, offset by offset amount
        :param payload:
        :return:
        """
        offset = 0
        data = json.loads(self.request.body)

        try:
            offset = int(data.get('offset'))
        except:
            pass

        user = Key(urlsafe=payload.get('userKey'))

        if user is None:
            return self.error(401)

        # user is here let's get their invites
        invites = Invite.query(Invite.to_player == user,
                               Invite.rejected == False,
                               Invite.accepted == False).fetch(limit=10, offset=offset)

        return self.response.write(json.dumps([{
                                                  "inviter": invite.from_player.urlsafe(),
                                                  "inviter_name": invite.from_player_name
                                              } for invite in invites]))


class CancelInviteHandler(request.RequestHandler):
    @decorators.jwt_required
    def post(self, payload):
        """
        Cancel the invite associated with the provided player keys
        :param payload:
        :return:
        """
        data = json.loads(self.request.body)
        user = Key(urlsafe=payload.get('userKey'))
        target_user = data.get('target_user')

        if target_user is None or target_user is '':
            return self.response.set_status(400, 'The target user was not provided')

        invite = Invite.query(Invite.from_player == user,
                               Invite.rejected == False,
                               Invite.accepted == False).get()

        if invite is None:
            invite = Invite.query(Invite.to_player == user,
                                  Invite.rejected == False,
                                  Invite.accepted == False).get()

        if invite is None:
            return self.response.set_status(400, 'No pending invites exist for these users')

        # let's cancel the invite
        try:
            invite.rejected = True
            invite.put()
            return self.error(200)
        except:
            return self.error(500)
