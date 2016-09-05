import jwt
import datetime


def encode_jwt(payload, key, algorithms='HS256', headers=None, json_encoder=None):
    """
    Encode the provided payload, using the specified settings
    :param payload: the dict to encode
    :param key: the secret key
    :param algorithms: the algorithm to use to encrypt the payload
    :param headers: we don't use the 'alg' header for security purposes
    :param json_encoder: the encoder to on the payload
    :return: the JWT containing the payload or None if it failed to encode
    """
    now = datetime.datetime.now()
    payload['exp'] = now + datetime.timedelta(days=3)
    payload['iat'] = now
    try:
        token = jwt.encode(payload, key, algorithms, headers, json_encoder)
    except Exception as e:
        print e.message
        return None

    return token


def decode_jwt(token, key, verify=True, algorithms='HS256', options=None):
    """
    Decode the provided token, using the specified settings.
    :param token: the JWT to decode
    :param key: the secret key
    :param verify: bool indicating whether the options should be considered when decoding
    :param algorithms: the algorithm used to encrypt the payload
    :param options: dict providing desired checks
    :return: the payload of the token if valid or None if it failed to decode
    """
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
