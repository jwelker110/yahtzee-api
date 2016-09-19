# Yahtzee!

The goal of this project is to implement a backend for a game that can be accessed by
client-side applications.

Explore the [API](https://yahtzee-142109.appspot.com/_ah/api/explorer).

Yahtzee! is a classic game providing endless hours of entertainment. The rules for this 
implementation are close to the [rules](https://en.wikipedia.org/wiki/Yahtzee#Rules) of
the original, with some minor changes.

The Yahtzee! bonus is treated as a joker, allowing the user to specify what they would
like to score, in addition to the extra 100 points!

### Frameworks/technologies used
- [Google App Engine](https://cloud.google.com/appengine/docs/python/)
- [PyJWT](https://pypi.python.org/pypi/PyJWT/1.4.2)
- [WebTest](https://webtest.readthedocs.io/en/latest/)

## Endpoints
- Prepend all endpoints with `/_ah/api/yahtzee/v1`
- **DateTime** values 
have been converted to [ISO 8601](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date)
dates.

##

#### Reauthorize JWT 
`/auth/reauth` - POST<br><br>
Should be called when the user navigates to the frontend. This will refresh the JWT by 
updating the expiration date. If the JWT is expired the user needs to log in with their Google account.
```
Example request:
{
    "jwt_token": string
}
Example response:
{
    "jwt_token": string
}
```
#### Register User
`/auth/user` - POST<br><br>
Verifies the identity of the user via Oauth using the auth code retrieved from a client side flow. If the
user already exists, we return a JWT with their claim. If they don't already exist, we create their
user in the datastore and return a JWT with their claim.<br><br>
**login_example.html** already implements the frontend flow to retrieve the user's
auth code and send to the server. The returned value is the JWT required for future requests.
```
Example request:
{
    "auth_code": string
}
Example response:
{
    "jwt_token": string
}
```
#### Create game invite
`/invite/create` - POST<br><br>
Provided the user does not have an active game with the provided player two, creates
an invite for player two. If player two has already invited the user to play a game, accepts the
invite and creates a game for them.
```
Example request:
{
    "jwt_token": string,
    "player_two_key": string
}
Example response (if invite accepted):
{
    "game_key": string,
    "game": Game JSON object
}
```
#### Retrieve game invites
`/invite/retrieve` - POST<br><br>
Retrieve the next 10 invites associated with the user starting from the provided 
offset, or 0.
```
Example request:
{
    "jwt_token": string,
    "offset": integer or 0
}
Example response:
{
    "invites": [{
        "inviter": string,
        "inviter_name": string
    }]
}
```
#### Cancel game invite
`/invite/cancel` - POST<br><br>
Cancel the invite associated with the target user.
```
Example request:
{
    "jwt_token": string,
    "target_user": string
}

```
#### Forfeit game
`/game/forfeit` - POST<br><br>
This will cancel the game associated with the provided game key.
```
Example request:
{
    "jwt_token": string,
    "game_key": string
}
```
#### Create new turn
`/turn/new` - POST<br><br>
Creates a new turn and rolls the dice for the first time.
```
Example request:
{
    "jwt_token": string,
    "game_key": string
}
Example response:
{
    "game_key": string,
    "turn_key": string,
    "roll_results": [integer],
    "turn_roll_count": integer
}
```
#### Take turn
`/turn/take` - POST<br><br>
Given game key and turn key, will locate the turn card for the user, and initiate a turn if there are < 13
turns. If the most recent turn contains empty rolls, this will expect a dice argument indicating which dice
to reroll. If a dice argument is not given, rerolls all dice.
```
Example request:
{
    "jwt_token": string,
    "game_key": string,
    "turn_key": string,
    "dice_to_roll": [integer]
}
Example response:
{
    "game_key": string,
    "turn_key": string,
    "roll_results": [integer],
    "turn_roll_count": integer
}
```
#### Complete turn
`/turn/complete` - POST<br><br>
This will complete the provided turn. Expects to get the string representation of the
cell to score e.g. "twos, sm_straight, full_house, etc...".
```
Example request:
{
    "jwt_token": string,
    "game_key": string,
    "allocate_to": string
}
```
#### View game details
`/game/view` - POST<br><br>
Retrieves the game matching the provided key, and returns the game details.
```
Example request:
{
    "jwt_token": string,
    "game_key": string
}
Example response:
{
    "game_key": string,
    "game": Game JSON object
}
```
#### Retrieve player game history
`/game/history` - POST<br><br>
Retrieves user's completed games starting from the provided offset, or 0. Limit 10.
```
Example request:
{
    "jwt_token": string,
    "offset": integer or 0
}
Example response:
{
    "games": [{
        "player_one": string,
        "player_two": string,
        "game_key": string
    }]
}
```
#### Retrieve game roll history
`/game/rolls` - POST<br><br>
Retrieves user's roll history for the provided game.
```
Example request:
{
    "jwt_token": string,
    "game_key": string
}
Example response:
{
    "rolls": [{
        "roll_one": [integer],
        "roll_two": [integer],
        "roll_three": [integer],
        "allocated_to": string,
        "date_completed": string
    }]
}
```
#### Retrieve current games
`/user/current` - POST<br><br>
Retrieves user's in-progress games starting from the provided offset, or 0. Limit 10.
```
Example request:
{
    "jwt_token": string,
    "offset": integer or 0
}
Example response:
{
    "games": [{
        "player_one": string,
        "player_two": string,
        "game_key": string
    }]
}
```
#### Get user ranks
`/user/rank` - GET<br><br>
Retrieve the 10 users with the most wins, ordered from highest to lowest.
```
Example response:
{
    "players": [{
        "username": string,
        "wins": integer
    }]
}
```
#### Get user high scores
`/user/highscore` - GET<br><br>
Retrieve the 10 users with highest scores in a single game, ordered from 
highest to lowest.
```
Example response:
{
    "players": [{
        "username": string,
        "score": integer
    }]
}
```
#### Get all users
`/user/all` - GET<br><br>
Return 10 users starting from the provided offset, or 0.
```
Example request:

offset=integer or 0

Example response:
{
    "players": [{
        "username": string,
        "user_key": string
    }]
}
```

#### Example Game JSON object
These values will **not** be in any kind of order like you see here.
```
{
  "player_one_name": "Tester01",
  "player_one_ones": "0",
  "player_one_twos": "0",
  "player_one_threes": "3",
  "player_one_fours": "4",
  "player_one_fives": "5",
  "player_one_sixes": "6",
  "player_one_upper_sub_total": "18",
  "player_one_bonus": "0",
  "player_one_upper_total": "18",
  "player_one_three_of_a_kind": "14",
  "player_one_four_of_a_kind": "0",
  "player_one_full_house": "0",
  "player_one_small_straight": "0",
  "player_one_large_straight": "0",
  "player_one_yahtzee": "0",
  "player_one_chance": "19",
  "player_one_lower_total": "33",
  "player_one_score_total": "51",
  "player_one_completed": True,
  "player_one_cancelled": False,
  "player_one_last_turn_date": "2016-09-19T13:19:22.531415",
  "player_two_name": "Tester02",
  "player_two_ones": "1",
  "player_two_twos": "6",
  "player_two_threes": "0",
  "player_two_fours": "8",
  "player_two_fives": "10",
  "player_two_sixes": "0",
  "player_two_upper_sub_total": "25",
  "player_two_bonus": "0",
  "player_two_upper_total": "25",
  "player_two_three_of_a_kind": "0",
  "player_two_four_of_a_kind": "0",
  "player_two_full_house": "0",
  "player_two_small_straight": "0",
  "player_two_large_straight": "0",
  "player_two_yahtzee": "0",
  "player_two_chance": "14",
  "player_two_lower_total": "14",
  "player_two_score_total": "39",
  "player_two_completed": True,
  "player_two_cancelled": False,
  "player_two_last_turn_date": "2016-09-19T13:19:22.571184",
  "date_created": "2016-09-19T18:19:19.718063",
  "winner_score": "51",
  "winner_name": "Tester01",
  "game_completed": True,
}
```
### Using the endpoints to play a game

1. Register the user, utilizing the code provided in **login_example.html**.
2. Retrieve a list of other users using `/user/all` so the user can find and select one 
to invite to play.
3. Once the user has found their opponent, use `/invite/create` to create an invitation
for that player to play.
4. To accept an invite, send a request to `/invite/create`, with the inviter's user_key
as the `player_two_key` value.
5. Once both users have accepted the invite, a game is automatically created for them.
The game will be returned to the user that accepts the invite automatically.
6. The inviter will need to send a request to `/user/current` to retrive the list of 
currently active games.
7. Now that both users have the `game_key`, they are able to begin rolling the dice.
8. At the start of every turn, users will need to send a request to `/turn/new` to
initiate a new turn and roll for the first time.
9. Once a turn has been created, send a request to `/turn/take` to roll the dice again.
Players will have a total of three rolls and must specify which dice to roll each time.
10. After the 3rd roll, the player will need to specify where they would like to allocate
their roll on their scorecard. Send a request to `/turn/complete` to assign the score.
11. Repeat steps 8-10 until 13 turns have been created and allocated.
12. At this point, the game will be complete for the player. The game will continue to
show not completed until both players have completed all their turns.

### Setting up the project

1. [Install](https://cloud.google.com/appengine/docs/python/download) Google App Engine SDK
2. [Clone](https://github.com/jwelker110/yahtzee-api.git) this repo.
3. [Install](https://pip.pypa.io/en/stable/installing/) Pip if you don't already have it.
4. Create a folder in the project named `lib`
5. `pip install -t lib --upgrade google-api-python-client WebTest PyJWT`
6. Check to ensure everything is installed correctly by running the provided tests `python runner.py`
7. Have fun!
