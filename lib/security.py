from Crypto.Hash import SHA256
from Crypto.Cipher import DES
from os import urandom

import logging
logging.getLogger().setLevel(logging.DEBUG)


HASH_REPS = 10000

VERY_GOOD_KEY = 'aBadKey!' # Needs to be 8 bytes for DES security

def __saltedhash(string, salt):
    sha256 = SHA256.new()
    sha256.update(string)
    sha256.update(salt)
    for x in xrange(HASH_REPS): 
        sha256.update(sha256.digest())
        if x % 10: sha256.update(salt)
    return sha256

def saltedhash_bin(string, salt=None):
    """returns the hash in binary format"""
    if salt == None:
        salt = urandom(16)
    return __saltedhash(string, salt).digest(), salt

def saltedhash_hex(string, salt=None):
    """returns the hash in hex format"""
    if salt == None:
        salt = urandom(16)
    return __saltedhash(string, salt).hexdigest(), salt

def encrypt(string):
    """ Pads the given string to be a multiple of 8 bytes and des-encrypts it. 
    Consequently does not work great for strings with leading blanks. """
    if string:
        des = DES.new(VERY_GOOD_KEY, DES.MODE_ECB)
        num_pad_bytes = 8 - len(string) % 8
        padded_string = "%%%ds" % num_pad_bytes % '' + string
        #logging.debug('Padded is ' +  padded_string + '.')
        return des.encrypt(padded_string)
    else:
        return string

def decrypt(string):
    """ Des decrypts and strips off leading blanks if any """

    #logging.debug('String be ' +  string + '.')
    if string:
        des = DES.new(VERY_GOOD_KEY, DES.MODE_ECB)
        try:
            return des.decrypt(string).strip()
        except ValueError:
            logging.debug('Could not decrypt: ' + string)
            return string
    else: 
        return string
