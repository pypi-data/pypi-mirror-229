import hashlib
import hmac
import base64
from time import time
from random import randint
from typing import Union


__author__ = '139928764+p4irin@users.noreply.github.com'
__version__ = '1.0.1'


def generate(
        username: Union[str, None]=None, shared_secret: str='',
        ttl: int=86400  # One day
    ) -> dict:

    """Generate ephemeral long term credentials.

    Ephemeral credentials are time limited. The credentials are used to
    authenticate the use of a TURN server. How to compute the credentials is
    described in 'A REST API For Access To TURN Services
    draft-uberti-behave-turn-rest-00'.

    Args:
        username: Optional. If not provided the username will be an int
             >= 10000 and <= 99999.
        shared_secret: Mandatory. A secret shared with a TURN server.
        ttl: the duration for which the username and password are valid,
            in seconds

    Returns:
        A dict with the keys 'turn_username' and 'turn_password'

    Raises:
        Exception('A secret you share with a TURN server is mandatory!'):
            A shared secret was not provided.
    """

    expiration_timestamp = int(time()) + ttl

    username = username if username else f'{randint(10000, 99999)}'
    if not shared_secret:
        raise Exception(
            'A secret you share with a TURN server is mandatory!'
        )
    turn_username = f'{expiration_timestamp}:{username}'

    dig = hmac.new(
        shared_secret.encode(), turn_username.encode(),
        hashlib.sha1
    ).digest()
    turn_password = base64.b64encode(dig).decode()

    return {
        "turn_username": turn_username,
        "turn_password": turn_password
    }
