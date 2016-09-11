import os
import jwt
import datetime


def encode_jwt(payload, key=None, algorithms='HS256', headers=None, json_encoder=None):
    """
    Encode the provided payload, using the specified settings
    :param payload: the dict to encode
    :param key: the secret key
    :param algorithms: the algorithm to use to encrypt the payload
    :param headers: we don't use the 'alg' header for security purposes
    :param json_encoder: the encoder to on the payload
    :return: the JWT containing the payload or None if it failed to encode
    """
    if key is None:
        key = os.environ.get('JWT_SECRET')

    now = datetime.datetime.now()
    payload['exp'] = now + datetime.timedelta(days=3)
    payload['iat'] = now
    try:
        token = jwt.encode(payload, key, algorithms, headers, json_encoder)
    except Exception as e:
        print e.message
        return None

    return token


def decode_jwt(token, key=None, verify=True, algorithms='HS256', options=None):
    """
    Decode the provided token, using the specified settings. Will raise LookupError if
    the JWT SECRET has not been set in the environment.
    :param token: the JWT to decode
    :param key: the secret key
    :param verify: bool indicating whether the options should be considered when decoding
    :param algorithms: the algorithm used to encrypt the payload
    :param options: dict providing desired checks
    :return: the payload of the token if valid or None if it failed to decode
    """
    if key is None:
        key = os.environ.get('JWT_SECRET')

    if key is None:
        raise LookupError('JWT_SECRET has not been set! Please set it before continuing')

    if options is None:
        options = {
                'verify_signature': True,
                'verify_exp': True,
                'verify_nbf': False,
                'verify_iat': True,
                'verify_aud': False,
                'verify_iss': False,
                'require_exp': True,
                'require_iat': True,
                'require_nbf': False
            }
    try:
        payload = jwt.decode(token, key, verify, algorithms, options)
    except Exception:
        return None

    return payload
