import endpoints

from ep import CompleteTurnHandler, NewTurnHandler, TakeTurnHandler, \
    CreateInviteHandler, RetrieveInviteHandler, CancelInviteHandler, \
    UserAllHandler, UserGamesHandler, UserRollHistoryHandler, UserGamesHistoryHandler, \
    ViewGameHandler, UserRankHandler, HighScoreHandler, CancelGameHandler, ReauthHandler, \
    UserHandler


app = endpoints.api_server([
    ViewGameHandler, TakeTurnHandler, NewTurnHandler, CompleteTurnHandler,
    CreateInviteHandler, RetrieveInviteHandler, CancelInviteHandler,
    UserGamesHistoryHandler, UserRollHistoryHandler, CancelGameHandler,
    UserGamesHandler, UserRankHandler, HighScoreHandler, UserAllHandler,
    UserHandler, ReauthHandler
])
