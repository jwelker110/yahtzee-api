import httplib2
import os
import endpoints

from protorpc import remote
from ep.endpoint_api import yahtzee_api
from messages import UserAuthFormRequest, UserAuthFormResponse
from google.appengine.ext.ndb import Key
from apiclient import discovery
from oauth2client import client
from models import User
from helpers import token


@yahtzee_api.api_class("auth")
class UserHandler(remote.Service):
    @endpoints.method(UserAuthFormRequest,
                      UserAuthFormResponse,
                      name="auth_user",
                      path="auth/user")
    def auth_user(self, request):
        """
        Verifies the identity of the user via Oauth using the user's auth code. If the
        user already exists, we return a JWT with their claim. If they don't already exist, we create their
        user in the datastore and return a JWT with their claim.
        """
        # we are using this application to make the request on behalf of the user
        client_id = os.environ.get('CLIENT_ID')
        client_secret = os.environ.get('CLIENT_SECRET')
        # code associated with the user so we can verify their identity
        auth_code = request.auth_code

        if client_secret is None:
            raise endpoints.InternalServerErrorException(
                'This application has not been configured with proper credentials')

        # make sure we actually have the keys
        if auth_code.replace(' ', '') == '':
            raise endpoints.BadRequestException('Auth code not provided')

        # verifying the user
        try:
            # we have the credentials associated with this client so
            # let's go ahead and verify the user using OAuth
            credentials = client.credentials_from_code(
                client_id,
                client_secret,
                'email',
                auth_code
            )
            http_auth = credentials.authorize(httplib2.Http())
            service = discovery.build('oauth2', 'v2', http=http_auth)
            userinfo = service.userinfo().get().execute()  # we should have the userinfo
        except:
            # were we given the wrong access token?
            raise endpoints.BadRequestException('Unable to authenticate access token. Verify the client ID is correct')

        # ok now create the user and jwt and pass it back!
        email = userinfo.get('email')

        if email is None:
            raise endpoints.BadRequestException('Unable to fetch email for this user')

        # check whether the user exists
        user = User.get_by_id(email)

        if user is None:
            try:
                # create the user
                username = email.split('@')[0]
                user = User(
                    username=username,
                    email=email
                )
                user.key = Key('User', email)
                user.put()
            except Exception as e:
                # print e.message
                raise endpoints.InternalServerErrorException('An error occurred while attempting to create user')

        # create the JWT and send it back to the user. This should
        # be used on all subsequent requests!
        payload = {
            "user_key": user.key.urlsafe()
        }

        try:
            jwt = token.encode_jwt(payload)
        except LookupError:
            raise endpoints.InternalServerErrorException('An error occurred while attempting to create credentials')

        return UserAuthFormResponse(
            jwt_token=jwt
        )
