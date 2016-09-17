import json
import random
import string

from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError

from helpers import request, decorators, exceptions
from models import Turn, TurnCard
from google.appengine.ext.ndb import Key
from datetime import datetime


class TakeTurnHandler(request.RequestHandler):
    @decorators.jwt_required
    def post(self, payload):
        """
        Given game key and turn key, will locate the turn card for the user, and initiate a turn if there are < 13
        turns. If the most recent turn contains empty rolls, this will expect a dice argument indicating which dice
        to reroll. If a dice argument is not given, rerolls all dice
        :param payload:
        :return: game key, turncard key, turn key, and the dice (array of dice values)
        """
        data = json.loads(self.request.body)
        game_key = data.get('game_key')
        turn_key = data.get('turn_key')
        dice_to_roll = data.get('dice_to_roll')

        try:
            user = Key(urlsafe=payload.get('userKey'))
            game = Key(urlsafe=game_key)
        except TypeError:
            return self.response.set_status(400, 'key was unable to be retrieved')
        except ProtocolBufferDecodeError:
            return self.response.set_status(400, 'key was unable to be retrieved')
        except Exception as e:
            return self.error(500)

        if user is None:
            # not sure how the JWT slipped through but they aren't authorized to do this
            return self.error(401)

        # get the turncard first, make sure it belongs to this user, then take the turn if possible else return
        # an error
        try:
            turncard = TurnCard.query(TurnCard.owner == user, TurnCard.game == game).get()
            if turncard is None:
                return self.error(400)

            if turncard.owner != user:
                return self.error(401)

            total_turns = len(turncard.turns)
            if total_turns == 0:
                return self.response.set_status(400, 'You need to start a new turn before you can roll')

            # the user owns this card, and there are still turns left. Let's take one
            current_turn = turncard.turns[total_turns - 1].get()

            if total_turns == 13:
                # check if the move has been allocated already
                if current_turn.allocated_to is not None:
                    return self.response.set_status(400, 'The game is already over')

                # check to make sure last turn is complete
                if len(current_turn.roll_three) != 0:
                    return self.response.set_status(400, 'You need to complete this turn to finish the game')

            # check if the current turn is completed, if it is, return error
            if current_turn.allocated_to is not None:
                return self.response.set_status(400, 'This turn has already been completed')

            # the turn hasn't been completed, so, make sure the dice to roll are in the previous roll, and then
            # roll the dice and assign them to the current roll
            roll_results = []
            turn_roll_count = 2

            if len(current_turn.roll_three) != 0:
                # turn needs to be completed
                return self.response.set_status(400, "You need to complete this turn")
            elif len(current_turn.roll_two) == 0:
                try:
                    roll_results = roll_dice(current_turn.roll_one, dice_to_roll)
                    current_turn.roll_two = roll_results
                except ValueError:
                    return self.response.set_status(400, 'Dice do not match previous roll')
                except:
                    return self.response.set_status(500, 'Error occurred while rolling')
            else:
                try:
                    roll_results = roll_dice(current_turn.roll_two, dice_to_roll)
                    current_turn.roll_three = roll_results
                    turn_roll_count = 3
                except ValueError:
                    return self.response.set_status(400, 'Dice do not match previous roll')
                except:
                    return self.response.set_status(500, 'Error occurred while rolling')

            turncard.turns[total_turns - 1] = current_turn.key
            turncard.put()

            return self.response.write(json.dumps({
                "game_key": game_key,
                "turn_key": turn_key,
                "roll_results": roll_results,
                "turn_roll_count": turn_roll_count
            }))

        except Exception as e:
            return self.error(500)


class NewTurnHandler(request.RequestHandler):
    @decorators.jwt_required
    def post(self, payload):
        """
        Takes the initial roll and adds the turn to the turncard.turns array
        :param payload:
        :return:
        """
        data = json.loads(self.request.body)
        game_key = data.get('game_key')

        try:
            user = Key(urlsafe=payload.get('userKey'))
            game = Key(urlsafe=game_key)
        except TypeError:
            return self.response.set_status(400, 'key was unable to be retrieved')
        except ProtocolBufferDecodeError:
            return self.response.set_status(400, 'key was unable to be retrieved')
        except Exception as e:
            return self.error(500)

        if user is None:
            # not sure how the JWT slipped through but they aren't authorized to do this
            return self.error(401)

        # we have the user and turncard just verify this is their turncard, verify the latest turn is complete, and
        # then create this new turn and add it to turncard.turns array
        try:
            turncard = TurnCard.query(TurnCard.owner == user, TurnCard.game == game).get()
            if turncard is None:
                return self.error(400)

            if turncard.owner != user:
                return self.error(401)

            total_turns = len(turncard.turns)

            if total_turns != 0:
                current_turn = turncard.turns[total_turns - 1].get()
                if total_turns == 13:
                    # check if the move has been allocated already
                    if current_turn.allocated_to is not None:
                        return self.response.set_status(400, 'The game is already over')

                    # check to make sure last turn is complete
                    if len(current_turn.roll_three) != 0:
                        return self.response.set_status(400, 'You need to complete this turn to finish the game')

                if current_turn.allocated_to is None:
                    return self.response.set_status(400, 'You need to finish this turn before starting a new one')

            roll_results = roll_dice([0, 0, 0, 0, 0], [0, 0, 0, 0, 0])
            new_turn = Turn(
                roll_one=roll_results,
                roll_two=[],
                roll_three=[]
            )
            new_turn.put()
            turncard.turns += [new_turn.key]
            turncard.put()

            return self.response.write(json.dumps({
                "game_key": game_key,
                "turn_key": new_turn.key.urlsafe(),
                "roll_results": roll_results,
                "turn_roll_count": 1
            }))
        except Exception as e:
            return self.error(500)


class CompleteTurnHandler(request.RequestHandler):
    @decorators.jwt_required
    def post(self, payload):
        """
        This will complete the provided turn. Expects to get the string representation of the
        cell to score e.g. "twos, sm_straight, full_house, etc..."
        :param payload:
        :return:
        """
        data = json.loads(self.request.body)
        game_key = data.get('game_key')
        allocate_to = data.get('allocate_to')

        try:
            user = Key(urlsafe=payload.get('userKey'))
            game = Key(urlsafe=game_key)
        except TypeError:
            return self.response.set_status(400, 'key was unable to be retrieved')
        except ProtocolBufferDecodeError:
            return self.response.set_status(400, 'key was unable to be retrieved')
        except Exception as e:
            return self.error(500)

        if user is None:
            # not sure how the JWT slipped through but they aren't authorized to do this
            return self.error(401)

        turncard = TurnCard.query(TurnCard.owner == user, TurnCard.game == game).get()
        if turncard is None:
            return self.error(400)

        if turncard.owner != user:
            return self.error(401)

        total_turns = len(turncard.turns)
        if total_turns < 1:
            return self.response.set_status(400, 'You should begin a turn before trying to complete one')
        # doesn't matter what turn this is, as long as it exists, and it hasn't been allocated, we can try to
        # allocate it to the game
        current_turn = turncard.turns[total_turns - 1].get()

        if current_turn.allocated_to is not None:
            return self.response.set_status(400, 'This turn has already been completed')

        try:
            game = game.get()
            if game is None:
                return self.response.set_status(400, 'This game does not exist')

            # game exists, so let's try to allocate this
            if game.player_one == user:
                score_player_one(allocate_to, game, current_turn)
            elif game.player_two == user:
                score_player_two(allocate_to, game, current_turn)
                game.player_two_last_turn_date = datetime.now()
            else:
                return self.response.set_status(400, 'The user provided is not associated with this game')

            game.put()
            return self.response.set_status(200)

        except exceptions.AlreadyAssignedError as e:
            return self.response.set_status(400, e.message)
        except Exception as e:
            print e.message
            return self.error(500)


def roll_dice(roll, dice_to_roll):
    """
    Create the random roll for the user
    :param roll: previous roll that contains dice we may want to keep
    :param dice_to_roll: the dice we are saying we want to reroll
    :return: the dice we wanted to save + the dice we rerolled
    """
    try:
        for die in dice_to_roll:
            roll.remove(die)
    except:
        raise ValueError('Provided dice do not match previous roll')

    dice_to_save = roll
    return dice_to_save + [random.randint(1, 6) for _ in xrange(0, len(dice_to_roll))]


def score_player_one(allocate_to, game, current_turn):
    """
    Attempts to allocate the roll to the desired scorecard category for player one
    :param allocate_to: the scorecard category
    :param game: the game with the scores
    :param current_roll: the dice that have been rolled for the turn
    """
    if len(current_turn.roll_three) == 0 and len(current_turn.roll_two) == 0:
        current_roll = current_turn.roll_one
    elif len(current_turn.roll_three) == 0:
        current_roll = current_turn.roll_two
    else:
        current_roll = current_turn.roll_three

    allocate_to = string.lower(allocate_to)
    exc = exceptions.AlreadyAssignedError('A score has already been assigned to that category')

    total = 0
    is_bonus_yahtzee = False

    # perform the bonus yahtzee check real quick
    if game.player_one_yahtzee > 0:
        die = current_roll[0]
        if current_roll == [die, die, die, die, die]:
            game.player_one_bonus_yahtzee += [100]
            is_bonus_yahtzee = True  # this lets them score it for any box

    if 'ones' == allocate_to:
        if game.player_one_ones is not None:
            raise exc
        game.player_one_ones = total_roll(current_roll, 1)

    elif 'twos' == allocate_to:
        if game.player_one_twos is not None:
            raise exc
        game.player_one_twos = total_roll(current_roll, 2)

    elif 'threes' == allocate_to:
        if game.player_one_threes is not None:
            raise exc
        game.player_one_threes = total_roll(current_roll, 3)

    elif 'fours' == allocate_to:
        if game.player_one_fours is not None:
            raise exc
        game.player_one_fours = total_roll(current_roll, 4)

    elif 'fives' == allocate_to:
        if game.player_one_fives is not None:
            raise exc
        game.player_one_fives = total_roll(current_roll, 5)

    elif 'sixes' == allocate_to:
        if game.player_one_sixes is not None:
            raise exc
        game.player_one_sixes = total_roll(current_roll, 6)

    elif 'three_of_a_kind' == allocate_to:
        if game.player_one_three_of_a_kind is not None:
            raise exc
        for _ in xrange(0, 3):
            die = current_roll[_]
            if current_roll[_:_ + 3] == [die, die, die]:  # goodness
                total = total_roll(current_roll)
                break
        game.player_one_three_of_a_kind = total

    elif 'four_of_a_kind' == allocate_to:
        if game.player_one_four_of_a_kind is not None:
            raise exc
        for _ in xrange(0, 2):
            die = current_roll[_]
            if current_roll[_:_ + 4] == [die, die, die, die]:  # I don't mean it I swear
                total = total_roll(current_roll)
                break
        game.player_one_four_of_a_kind = total

    elif 'full_house' == allocate_to:
        if game.player_one_full_house is not None:
            raise exc
        low = current_roll[0]
        high = current_roll[4]
        game.player_one_full_house = 25 if [low, low, high, high, high] == current_roll \
                                           or [low, low, low, high, high] == current_roll \
                                           or is_bonus_yahtzee else 0

    elif 'small_straight' == allocate_to:
        if game.player_one_small_straight is not None:
            raise exc
        for _ in xrange(0, 2):
            die = current_roll[_]
            if current_roll[_:_ + 4] == [die, die + 1, die + 2, die + 3] or is_bonus_yahtzee:
                total = 30
                break
        game.player_one_small_straight = total

    elif 'large_straight' == allocate_to:
        if game.player_one_large_straight is not None:
            raise exc
        die = current_roll[0]
        game.player_one_large_straight = 40 if current_roll == [die, die + 1, die + 2, die + 3, die + 4] \
                                               or is_bonus_yahtzee else 0

    elif 'yahtzee' == allocate_to:
        if game.player_one_yahtzee == 0:  # already been zeroed out sorrrrrryyyy
            raise exc
        die = current_roll[0]
        game.player_one_yahtzee = 50 if current_roll == [die, die, die, die, die] else 0

    elif 'chance' == allocate_to:
        if game.player_one_chance is not None:
            raise exc
        game.player_one_chance = total_roll(current_roll)
    else:
        return False

    game.player_one_last_turn_date = datetime.now()
    current_turn.date_completed = datetime.now()
    current_turn.allocated_to = allocate_to


def score_player_two(allocate_to, game, current_turn):
    """
    Attempts to allocate the roll to the desired scorecard category for player two
    :param allocate_to: the scorecard category
    :param game: the game with the scores
    :param current_roll: the dice that have been rolled for the turn
    :return:
    """
    if len(current_turn.roll_three) == 0 and len(current_turn.roll_two) == 0:
        current_roll = current_turn.roll_one
    elif len(current_turn.roll_three) == 0:
        current_roll = current_turn.roll_two
    else:
        current_roll = current_turn.roll_three

    allocate_to = string.lower(allocate_to)
    exc = exceptions.AlreadyAssignedError('A score has already been assigned to that category')

    total = 0
    is_bonus_yahtzee = False

    # perform the bonus yahtzee check real quick
    if game.player_two_yahtzee > 0:
        die = current_roll[0]
        if current_roll == [die, die, die, die, die]:
            game.player_two_bonus_yahtzee += [100]
            is_bonus_yahtzee = True  # this lets them score it for any box

    if 'ones' == allocate_to:
        if game.player_two_ones is not None:
            raise exc
        game.player_two_ones = total_roll(current_roll, 1)

    elif 'twos' == allocate_to:
        if game.player_two_twos is not None:
            raise exc
        game.player_two_twos = total_roll(current_roll, 2)

    elif 'threes' == allocate_to:
        if game.player_two_threes is not None:
            raise exc
        game.player_two_threes = total_roll(current_roll, 3)

    elif 'fours' == allocate_to:
        if game.player_two_fours is not None:
            raise exc
        game.player_two_fours = total_roll(current_roll, 4)

    elif 'fives' == allocate_to:
        if game.player_two_fives is not None:
            raise exc
        game.player_two_fives = total_roll(current_roll, 5)

    elif 'sixes' == allocate_to:
        if game.player_two_sixes is not None:
            raise exc
        game.player_two_sixes = total_roll(current_roll, 6)

    elif 'three_of_a_kind' == allocate_to:
        if game.player_two_three_of_a_kind is not None:
            raise exc
        for _ in xrange(0, 3):
            die = current_roll[_]
            if current_roll[_:_ + 3] == [die, die, die]:  # goodness
                total = total_roll(current_roll)
                break
        game.player_two_three_of_a_kind = total

    elif 'four_of_a_kind' == allocate_to:
        if game.player_two_four_of_a_kind is not None:
            raise exc
        for _ in xrange(0, 2):
            die = current_roll[_]
            if current_roll[_:_ + 4] == [die, die, die, die]:  # I don't mean it I swear
                total = total_roll(current_roll)
                break
        game.player_two_four_of_a_kind = total

    elif 'full_house' == allocate_to:
        if game.player_two_full_house is not None:
            raise exc
        low = current_roll[0]
        high = current_roll[4]
        game.player_two_full_house = 25 if [low, low, high, high, high] == current_roll \
                                           or [low, low, low, high, high] == current_roll \
                                           or is_bonus_yahtzee else 0

    elif 'small_straight' == allocate_to:
        if game.player_two_small_straight is not None:
            raise exc
        for _ in xrange(0, 2):
            die = current_roll[_]
            if current_roll[_:_ + 4] == [die, die + 1, die + 2, die + 3] or is_bonus_yahtzee:
                total = 30
                break
        game.player_two_small_straight = total

    elif 'large_straight' == allocate_to:
        if game.player_two_large_straight is not None:
            raise exc
        die = current_roll[0]
        game.player_two_large_straight = 40 if current_roll == [die, die + 1, die + 2, die + 3, die + 4] \
                                               or is_bonus_yahtzee else 0

    elif 'yahtzee' == allocate_to:
        if game.player_two_yahtzee == 0:  # already been zeroed out sorrrrrryyyy
            raise exc
        die = current_roll[0]
        game.player_two_yahtzee = 50 if current_roll == [die, die, die, die, die] else 0

    elif 'chance' == allocate_to:
        if game.player_two_chance is not None:
            raise exc
        game.player_two_chance = total_roll(current_roll)
    else:
        return False

    game.player_two_last_turn_date = datetime.now()
    current_turn.date_completed = datetime.now()
    current_turn.allocated_to = allocate_to


def total_roll(roll, target=None):
    """
    Sums the roll, only summing dice that match the target, if given, else summing all the dice
    :param roll: the dice
    :param target: the number that if matched should be added to the sum
    :return:
    """
    total = 0

    if target is None:
        for die in roll:
            total += die
    else:
        for die in roll:
            total += die if die == target else 0

    return total
