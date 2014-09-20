from google.appengine.ext import db

from lib.security import encrypt, decrypt

import logging
logging.getLogger().setLevel(logging.DEBUG)

USER_INT_PROPERTIES = set(('expiration', 'wins', 'losses', 'credits', 
                           'level', 'experience', 'status'))
USER_VERIFIED = 0
USER_UNVERIFIED = 1

USER_VERIFY_MAP = {USER_VERIFIED:"Verified", USER_UNVERIFIED:"Unverified"}

class GameUser(db.Model):
    """ Models an authenticated user """
    
    name = db.StringProperty()
    password = db.ByteStringProperty()
    game = db.StringProperty()
    salt = db.ByteStringProperty()
    token = db.StringProperty()
    expiration = db.IntegerProperty()
    status = db.IntegerProperty(default = 0)
    verification = db.StringProperty()

    create_date = db.DateTimeProperty(auto_now_add=True)
    modify_date = db.DateTimeProperty(auto_now_add=True)
    last_login_date = db.DateTimeProperty(auto_now_add=True)

    email = db.ByteStringProperty()
    phone = db.ByteStringProperty()

    wins = db.IntegerProperty(default = 0)
    losses = db.IntegerProperty(default = 0)
    credits = db.IntegerProperty(default = 0)
    level = db.IntegerProperty(default = 0)
    experience = db.IntegerProperty(default = 0)
    blob = db.TextProperty()

    def set_value(self, property, value):
        if property in USER_INT_PROPERTIES:
            logging.debug("Setting %s to %s" % (property, value))
            setattr(self, property, int(value))
        else:
            logging.debug("Setting %s to %s" % (property, value))
            setattr(self, property, str(value))

    def to_dict(self):
        dicty = {}

        # Handle date properties
        for property in ("create_date", "modify_date", "last_login_date"):
            dicty[property] = str(getattr(self, property))

        # Handle encrypted properties
        for property in ('email', 'phone'):
            dicty[property] = decrypt(getattr(self, property))
            logging.debug('Property ' + property + ' is:' + dicty[property])

        # Handle rest of visible properties
        for property in ('name', 'game', 'wins', 'losses', 'credits', 
                         'level', 'experience', 'blob'):
            dicty[property] = getattr(self, property)

        dicty['status'] = USER_VERIFY_MAP[self.status]

        return dicty

    @classmethod 
    def get_by_verification(cls, verification):
        return db.GqlQuery("SELECT * from GameUser WHERE verification = :1", verification)


    @classmethod
    def get_by_name(cls, name, game):
        """ Returns the first user for the given game with the given name.  
        """

        users = db.GqlQuery("SELECT * from GameUser WHERE name = :1 and game = :2", name.lower(), game)

        if users.count() > 1:
            logging.error("More than one user with name: %s" % name)

        user = None
        for user in users:
            break

        return user


    @classmethod
    def name_is_available(cls, name, game):
        """ Returns true if the given user name has not been used in the given
            game.
        """
        users = db.GqlQuery("SELECT * from GameUser WHERE name = :1 and game = :2", name.lower(), game)
        return users.count() == 0

    @classmethod
    def email_is_available(cls, email, game):
        """ Returns true if the given email address has not been used in the given
            game.
        """
        return True
        users = db.GqlQuery("SELECT name from GameUser WHERE email = :1 and game = :2", email, game)
        return users.count() == 0


    @classmethod
    def list(cls, game):
        return db.GqlQuery("SELECT * FROM GameUser WHERE game = :1", game)


class GameItem(db.Model):
    """ Models an item that a user possesses 
    """

    user = db.ReferenceProperty(GameUser)
    itemtype = db.StringProperty()
    name = db.StringProperty()
    quantity = db.IntegerProperty()
    create_date = db.DateTimeProperty(auto_now_add=True)
    blob = db.TextProperty()

    @classmethod
    def get(cls, user, itemtype, name):
        """ Returns the first item for the given user with the given name and type
        """
        items = db.GqlQuery("SELECT * from GameItem WHERE user = :1 and name = :2 and itemtype = :3", user, name, itemtype)

        item = None
        if items.count() > 1:
            logging.error("More than one item for user %s with type %s and name %s" %
                          (user.name, itemtype, name))
        for item in items:
            break

        return item


    @classmethod
    def list(cls, user):
        return db.GqlQuery("SELECT * FROM GameItem WHERE user = :1 order by create_date", user)


    def to_dict(self):
        dicty = {}
        for property in ('itemtype', 'name', 'quantity', 'blob'):
            dicty[property] = getattr(self, property)
        return dicty

