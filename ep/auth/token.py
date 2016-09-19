import endpoints
import datetime

from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from protorpc import remote
from ep.endpoint_api import yahtzee
from messages import ReauthForm
from helpers import token
from google.appengine.ext.ndb import Key


@yahtzee.api_class("auth")
class ReauthHandler(remote.Service):
    @endpoints.method(ReauthForm,
                      ReauthForm,
                      name="reauth",
                      path="auth/reauth")
    def reauth(self, request):
        """
        JWT required. Should be called when the user navigates to the frontend. This will refresh the jwt by
        updating the expiration date. If the jwt is expired the user needs to hit the User ep to obtain a new token
        by logging in with their Google account
        """
        payload = token.decode_jwt(request.jwt_token)
        jwt_token = token.encode_jwt(payload=payload)

        try:
            user = Key(urlsafe=payload.get('user_key')).get()
            if user is not None:
                user.last_active = datetime.datetime.utcnow()
                user.put()
        except TypeError:
            raise endpoints.BadRequestException('key was unable to be retrieved')
        except ProtocolBufferDecodeError:
            raise endpoints.BadRequestException('key was unable to be retrieved')
        except Exception as e:
            raise endpoints.InternalServerErrorException('An error occurred when attempting to take the turn')

        return ReauthForm(
            jwt_token=jwt_token
        )
