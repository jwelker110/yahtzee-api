import json

from functools import wraps
from helpers import token


def jwt_required(func):
    """
    This decorator will pass the JWT payload to the function it is wrapping, else it will return a 401 UNAUTHORIZED.
    :param func: function to wrap
    :return: wrapper function
    """
    @wraps(func)
    def wrapper(self):
        if self.request.body is None or self.request.body is '':
            return self.response.set_status(400, 'Please include the token with the request')
        try:
            data = json.loads(self.request.body)
        except ValueError:
            return self.response.set_status(500, 'An error occurred while processing your request. '
                                                 'Check your request body and try again')
        except:
            return self.error(500)
        jwt_token = data.get('jwt_token')
        payload = token.decode_jwt(jwt_token)
        if payload is '' or payload is None:
            return self.error(401)
        func(self, payload)
    return wrapper
