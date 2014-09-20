import time, random
try:
    import json
except:
    from django.utils import simplejson as json

DEFAULT_EXPIRATION = 300  # 5 minutes
MAX_EXPIRATION = 86400    # 1 day

TOKEN_KEY = 'Thisisnotsecure'

def get_token_str():
    return '%16x' % random.randrange(256**8)

def get_token_expiration(expiration):
    # Don't let expiration be zero or greater than the MAX_EXPIRATION
    if expiration == 0:
        expiration = DEFAULT_EXPIRATION
    expiration = min(expiration, MAX_EXPIRATION)
    return expiration

def pack(user, expiration=DEFAULT_EXPIRATION):
    """ Packs the user name and expiration time into a dict, jsonifies it,
    and then does a cheesy bit-wise OR with a "secret" key on the json
    """

    # Don't let expiration be zero or greater than the MAX_EXPIRATION
    if expiration == 0:
        expiration = DEFAULT_EXPIRATION
    expiration = min(expiration, MAX_EXPIRATION)

    token_dict = dict(user=user, expiration=expiration + int(time.time()))
    token_str = json.dumps(token_dict)
    token = ""
    for pos in xrange(len(token_str)):
        bias = ord(TOKEN_KEY[pos % len(TOKEN_KEY)])
        token += chr(ord(token_str[pos]) ^ bias)
    return token


def unpack(token):
    """ Returns the user name and expiration time from the encoded token """
    token_str = ""
    for pos in xrange(len(token)):
        bias = ord(TOKEN_KEY[pos % len(TOKEN_KEY)])
        token_str += chr(ord(token[pos]) ^ bias)
    try:
        token_dict = json.loads(token_str)
        user, expiration = token_dict['user'], token_dict['expiration']
    except:
        user, expiration = None, 0

    return user, expiration

def is_valid(token, user):
    token_user, token_expiration = unpack(token)
    return token_expiration > time.time() and user == token_user

        
