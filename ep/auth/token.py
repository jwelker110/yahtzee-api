import json
from helpers import request, token, decorators


class ReauthHandler(request.RequestHandler):
    @decorators.jwt_required
    def post(self, payload):
        """
        This will refresh the jwt by updating the expiration date. If the jwt is expired
        the user needs to hit the User ep to obtain a new token.
        :param payload: the original payload
        :return: refreshed JWT
        """
        jwt_token = token.encode_jwt(payload=payload)
        return self.response.write(json.dumps({
            "jwt_token": jwt_token
        }))
