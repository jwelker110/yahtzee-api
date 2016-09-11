import json

from helpers import request, decorators
from models import Game, Invite, TurnCard
from google.appengine.ext.ndb import Key


class InviteHandler(request.RequestHandler):
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

        data = json.loads(self.request.body)
        player_two_key = data.get('player_two_key')

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
            Game.player_one == payload.get('userKey'),
            Game.player_two == player_two_key,
            Game.completed == False).get()

        if game is None:
            game = Game.query(Game.player_one == player_two_key,
                              Game.player_two == payload.get('userKey'),
                              Game.completed == False).get()

        # if a game exists between these users, they need to finish it first please
        if game is not None:
            # not entirely certain what to set here, as the request wasn't necessarily wrong, but the
            # user already has a game with player_two
            return self.response.set_status(400, "An existing game must be finished before starting another one")

        # let's check for an existing invite between these players
        invite = Invite.query(
            Invite.from_player == payload.get('userKey'),
            Invite.to_player == player_two_key,
            Invite.accepted == False,
            Invite.rejected == False
        ).get()

        if invite is not None:
            return self.response.set_status(400, "A pending invite must be accepted or declined before creating another one")

        invite = Invite.query(
            Invite.from_player == player_two_key,
            Invite.to_player == payload.get('userKey'),
            Invite.accepted == False,
            Invite.rejected == False
        ).get()

        if invite is not None:
            # awesome! the inviter already has an invitation from the invitee.
            # start a game, and create the turncards for each player
            try:
                game = Game(
                    player_one=player_two_key,
                    player_two=payload.get('userKey')
                )
                player_one_turncard = TurnCard(
                    owner=payload.get('userKey'),
                    game=game.key.urlsafe()
                )
                player_two_turncard = TurnCard(
                    owner=player_two_key,
                    game=game.key.urlsafe()
                )
                player_one_turncard.put()
                player_two_turncard.put()
                game.put()
            except:
                return self.response.set_status(500, 'An error occurred while attempting to create a game')

            #
            return self.response.write(json.dumps({
                "game_key": game.key.urlsafe(),
                "game": game.to_dict()
            }))

        # alright there are no invites between these players yet so let's make one
        try:
            invite = Invite(
                from_player=payload.get('userKey'),
                to_player=player_two_key
            )
            invite.put()
            return self.response.set_status(200)
        except:
            return self.response.set_status(500, 'An error occurred while attempting to create an invite')
