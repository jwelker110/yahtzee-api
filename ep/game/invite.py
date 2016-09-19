import json
import endpoints

from messages import CreateInviteRequestForm, CreateInviteResponseForm, CancelInviteRequestForm, \
    RetrieveInviteRequestForm, RetrieveInviteResponseForm, InviteForm
from protorpc import remote, message_types
from ep.endpoint_api import yahtzee
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from helpers import token
from models import Game, Invite, TurnCard
from google.appengine.ext.ndb import Key


@yahtzee.api_class("game")
class CreateInviteHandler(remote.Service):
    @endpoints.method(CreateInviteRequestForm,
                      CreateInviteResponseForm,
                      name="create_invite",
                      path="invite/create")
    def create_invite(self, request):
        """
        JWT required. Provided the user does not have an active game with the provided player two, creates
        an invite for player two. If player two has already invited the user to play a game, accepts the
        invite and creates a game for them.

        If a game is created, the user will be able to retrieve it from game endpoint and begin playing.
        """
        player_two_key = request.player_two_key
        payload = token.decode_jwt(request.jwt_token)

        try:
            user = Key(urlsafe=payload.get('user_key')).get()
            # grab player two please
            player_two = Key(urlsafe=player_two_key).get()
        except TypeError:
            raise endpoints.BadRequestException('key was unable to be retrieved')
        except ProtocolBufferDecodeError:
            raise endpoints.BadRequestException('key was unable to be retrieved')
        except Exception as e:
            raise endpoints.InternalServerErrorException('An error occurred when attempting to take the turn')

        if player_two is None:
            raise endpoints.BadRequestException('Player does not exist')

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
            raise endpoints.BadRequestException("An existing game must be finished before starting another one")

        # let's check for an existing invite between these players
        invite = Invite.query(
            Invite.from_player == user.key,
            Invite.to_player == player_two.key,
            Invite.accepted == False,
            Invite.rejected == False
        ).get()

        if invite is not None:
            raise endpoints.BadRequestException(
                "A pending invite must be accepted or declined before creating another one")

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
                    player_one_name=player_two.username,
                    player_two=user.key,
                    player_two_name=user.username
                )
                game.put()
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

                return CreateInviteResponseForm(
                    game_key=game.key.urlsafe(),
                    game=game.to_form()
                )

            except Exception as e:
                # print e.message
                raise endpoints.InternalServerErrorException('An error occurred while attempting to create a game')

        # alright there are no invites between these players yet so let's make one
        try:
            invite = Invite(
                from_player=user.key,
                from_player_name=user.username,
                to_player=player_two.key,
                to_player_name=player_two.username
            )
            invite.put()
            return CreateInviteResponseForm()
        except:
            raise endpoints.InternalServerErrorException('An error occurred while attempting to create an invite')


@yahtzee.api_class("game")
class RetrieveInviteHandler(remote.Service):
    @endpoints.method(RetrieveInviteRequestForm,
                      RetrieveInviteResponseForm,
                      name="retrieve_invite",
                      path="invite/retrieve")
    def retrieve_invite(self, request):
        """
        JWT required. Retrieve the next 10 invites associated with the user starting from the provided offset, or 0
        """
        offset = request.offset
        payload = token.decode_jwt(request.jwt_token)

        try:
            user = Key(urlsafe=payload.get('user_key'))
        except TypeError:
            raise endpoints.BadRequestException('key was unable to be retrieved')
        except ProtocolBufferDecodeError:
            raise endpoints.BadRequestException('key was unable to be retrieved')
        except Exception as e:
            raise endpoints.InternalServerErrorException('An error occurred when attempting to take the turn')

        # user is here let's get their invites
        invites = Invite.query(Invite.to_player == user,
                               Invite.rejected == False,
                               Invite.accepted == False).fetch(limit=10, offset=offset)
        return RetrieveInviteResponseForm(
            invites=[InviteForm(
                inviter=invite.from_player.urlsafe(),
                inviter_name=invite.from_player_name
            ) for invite in invites]
        )


@yahtzee.api_class("game")
class CancelInviteHandler(remote.Service):
    @endpoints.method(CancelInviteRequestForm,
                      message_types.VoidMessage,
                      name="cancel_invite",
                      path="invite/cancel")
    def cancel_invite(self, request):
        """
        JWT required. Cancel the invite associated with the user
        """
        target_user = request.target_user
        payload = token.decode_jwt(request.jwt_token)

        try:
            user = Key(urlsafe=payload.get('user_key'))
        except TypeError:
            raise endpoints.BadRequestException('key was unable to be retrieved')
        except ProtocolBufferDecodeError:
            raise endpoints.BadRequestException('key was unable to be retrieved')
        except Exception as e:
            raise endpoints.InternalServerErrorException('An error occurred when attempting to take the turn')

        if target_user is None or target_user is '':
            raise endpoints.BadRequestException('The target user was not provided')

        invite = Invite.query(Invite.from_player == user,
                               Invite.rejected == False,
                               Invite.accepted == False).get()

        if invite is None:
            invite = Invite.query(Invite.to_player == user,
                                  Invite.rejected == False,
                                  Invite.accepted == False).get()

        if invite is None:
            raise endpoints.BadRequestException('No pending invites exist for these users')

        # let's cancel the invite
        try:
            invite.rejected = True
            invite.put()
            return message_types.VoidMessage()
        except:
            raise endpoints.InternalServerErrorException('An error occurred while attempting to cancel the invite')
