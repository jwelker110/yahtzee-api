import json
import endpoints

from protorpc import remote, message_types
from ep.endpoint_api import yahtzee_api
from messages import ReauthForm
from helpers import token


@yahtzee_api.api_class("auth")
class ReauthHandler(remote.Service):
    @endpoints.method(ReauthForm,
                      ReauthForm,
                      name="reauth",
                      path="auth/reauth")
    def reauth(self, request):
        """
        This will refresh the jwt by updating the expiration date. If the jwt is expired
        the user needs to hit the User ep to obtain a new token.
        """
        payload = token.decode_jwt(request.jwt_token)
        jwt_token = token.encode_jwt(payload=payload)

        return ReauthForm(
            jwt_token=jwt_token
        )
