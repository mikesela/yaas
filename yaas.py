from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import mail
try:
    import json
except:
    from django.utils import simplejson as json
import logging

import random
import string
from datetime import datetime, timedelta

from model import GameUser, GameItem, USER_VERIFIED, USER_UNVERIFIED
from lib.utils import missing_keys, write_response
from lib.decorators import validate_inputs
from lib.security import saltedhash_hex, encrypt, decrypt
from lib.token import get_token_str, get_token_expiration

GET_ENABLED = True

GAMES = {"testgame":  {"name":"Test Game",
                       "emailVerification":False}}

#json_date_handler = lambda obj: obj.isoformat() if isinstance(obj, datetime) else None


#last used error code: 14


class LoginHandler(webapp.RequestHandler):
    """  Logs a user in and returns a time-limited token which is a required input
         for other APIs.  If caller does not specify an expiration time, the 
         token will be generated with the default expiration
    
    Input:
          fields         : name, password, gameid
          optional fields: expiration (in seconds)

          example: /user/login?expiration=5&password=aPassword&name=aUserName&gameid=j18dx2ll8

    Output:
          fields: token

          example: {'status': 0,
                    'data'  : {'token': 'e37600a5628abfc3'}} 

    Error Statuses:
          1: Required input fields are missing
          4: Gameid is invalid
          3: User name or password is invalid
          5: Gameid incorrect for this user
    """

    def get(self):
        if GET_ENABLED:
            return self.post()
        else:
            write_response(self.response, "10", None, "GET not enabled.")

    @validate_inputs(required=['name', 'password', 'gameid'])
    def post(self):
        logging.debug("In LoginHandler")
        self.response.headers['Content-Type'] = 'application/json'

        # Verify the gameid is valid:
        gameid = self.request.get('gameid')
        if gameid not in GAMES:
            write_response(self.response, "4", None, "Gameid is invalid.")
            return

        # Ensure name is valid
        name = self.request.get('name')
        user = GameUser.get_by_name(name, GAMES[gameid]['name'])
        if not user:
            write_response(self.response, "3", None, 
                           "User name or password is invalid.")
            return

        # Ensure password matches one in DB
        password = self.request.get('password')
        encrypted_password,  salt = saltedhash_hex(password, user.salt)
        if encrypted_password != user.password:
            write_response(self.response, "3", None, 
                           "User name or Password is incorrect.")
            return

        # Ensure game matches one in DB
        game = GAMES[gameid]['name']
        if game != user.game:
            write_response(self.response, "5", None, 
                           "Gameid incorrect for this user %s." % name)
            return

        # Ensure user is verified
        if user.status == USER_UNVERIFIED:
            write_response(self.response, "14", None, 
                           "User %s is unverified." % name)
            return

        #Generate token
        token = get_token_str()
        expiration = get_token_expiration(int(self.request.get('expiration', 0)))
        user.last_login_date = datetime.now()
        user.token = token
        user.expiration = expiration
        user.put()

        write_response(self.response, "0", json.dumps(dict(token=token)))

class ListUserHandler(webapp.RequestHandler):
    """  Lists all the users for this game.
    
    Input:
          fields: gameid

          example: /user/list?gameid=j18dx2ll8

    Output:
          List of user dictionaries

          example: {'data': [{'create_date': '2011-10-02 17:36:13.532114',
                              'credits': 0,
                              'email': '',
                              'experience': 0,
                              'game': 'testgame',
                              'last_login_date': '2011-10-04 00:35:15.528540',
                              'level': 0,
                              'losses': 0,
                              'modify_date': '2011-10-02 22:31:40.068998',
                              'name': 'Mikes1',
                              'phone': '415-123-4568',
                              'blob': 'asdf1234'
                              'wins': 0},
                             {'create_date': '2011-10-10 02:17:47.514796',
                              'credits': 0,
                              'email': '',
                              'experience': 0,
                              'game': 'testgame',
                              'last_login_date': '2011-10-10 02:17:47.514876',
                              'level': 0,
                              'losses': 0,
                              'modify_date': '2011-10-10 02:17:47.514812',
                              'name': 'aUserName',
                              'phone': '',
                              'blob': 'asdf1234'
                              'wins': 0}],
                   'status': 0}

    Error Statuses:
          1: Required input fields are missing
          4: Gameid is invalid

          """

    def get(self):
        if GET_ENABLED:
            return self.post()
        else:
            write_response(self.response, "10", None, "GET not enabled")
        
    @validate_inputs(required=['gameid'])
    def post(self):
        logging.debug("In ListUserHandler")
        self.response.headers['Content-Type'] = 'application/json'

        # Verify the gameid is valid:
        gameid = self.request.get('gameid')
        if gameid not in GAMES:
            write_response(self.response, "4", None, "Gameid is invalid: %s" % gameid)
            return

        userlist = []
        users = GameUser.list(GAMES[gameid]['name'])
        for user in users:
            userdict = user.to_dict()
            userlist.append(userdict)

        write_response(self.response, "0", json.dumps(userlist))
                            

class DeleteUserHandler(webapp.RequestHandler):
    """  Deletes a user for this game.
    
    Input:
          fields: gameid, name

          example: /user/delete?gameid=j18dx2ll8&name=aUserName

    Output:
          None

          example: {'data': {}, 'status': 0}

    Error Statuses:
          1: Required input fields are missing
          4: Gameid is invalid
          6: User does not exist

          """

    def get(self):
        if GET_ENABLED:
            return self.post()
        else:
            write_response(self.response, "10", None, "GET not enabled")

    @validate_inputs(required=['name', 'gameid'])
    def post(self):
        logging.debug("In DeleteUserHandler")
        self.response.headers['Content-Type'] = 'application/json'

        # Verify the gameid is valid:
        gameid = self.request.get('gameid')
        if gameid not in GAMES:
            write_response(self.response, "4", None, "gameid is invalid: %s" % gameid)
            return

        # Get the user
        name = self.request.get('name')
        game = GAMES[self.request.get('gameid')]['name']
        user = GameUser.get_by_name(name, game)
        if not user:
            write_response(self.response, "6", None, "User %s does not exist" % name)
            return

        user.delete()
        write_response(self.response, "0", {})

class UpdateUserHandler(webapp.RequestHandler):
    """  Updates a user
    
    Input:
          fields         : gameid, name, token
          optional fields: email, phone, wins, losses, credits, level, 
                           experience, blob

          example: /user/update?gameid=j18dx2ll8&name=aUserName&credits=3&wins=1&losses=2&experience=5&phone=(123)456-7890&token=1c40d1991684f1dd&level=4&email=testing@email.com

    Output:
          None

          example: {'data': {}, 'status': 0}

    Error Statuses:
          1: Required input fields are missing
          4: Gameid is invalid
          6: User does not exist
          7: Token is invalid
          8: Token has expired

          """

    def get(self):
        if GET_ENABLED:
            return self.post()
        else:
            write_response(self.response, "10", None, "GET not enabled")

    @validate_inputs(required=['token', 'name', 'gameid'])
    def post(self):
        logging.debug("In UpdateUserHandler")
        self.response.headers['Content-Type'] = 'application/json'

        # Do basic update validation
        user = get_user_for_update(self.request, self.response)
        if user == None:
            return

        request_args = set(self.request.arguments())

        # Update encrypted fields
        for property in ('email', 'phone'):
            if property in request_args:
                user.set_value(property, encrypt(self.request.get(property)))

        # Update rest of fields
        for property in ('wins', 'losses', 'credits', 
                         'level', 'experience', 'blob'):

            if property in request_args:
                user.set_value(property, self.request.get(property))

        user.modify_date = datetime.now()
        user.put()

        write_response(self.response, "0", {})


class GetUserHandler(webapp.RequestHandler):
    """  Lists all the users for this game.
    
    Input:
          fields: gameid, name, token

          example: /user/get?token=1c40d1991684f1dd&gameid=j18dx2ll8&name=aUserName

    Output:
          A user dictionary (name, email, etc)

          example: {'data': {'create_date': '2011-10-10 02:17:54.360349',
                             'credits': 3,
                             'email': 'testing@email.com',
                             'experience': 5,
                             'game': 'testgame',
                             'last_login_date': '2011-10-10 02:17:54.512005',
                             'level': 4,
                             'losses': 2,
                             'modify_date': '2011-10-10 02:17:54.558967',
                             'name': 'aUserName',
                             'phone': '(123)456-7890',
                             'blob': 'asdf1234'
                             'wins': 1},
                   'status': 0}

    Error Statuses:
          1: Required input fields are missing
          4: Gameid is invalid
          6: User does not exist
          """

    def get(self):
        if GET_ENABLED:
            return self.post()
        else:
            write_response(self.response, "10", None, "GET not enabled")

    @validate_inputs(required=['token', 'name', 'gameid'])
    def post(self):
        logging.debug("In GetUserHandler")
        self.response.headers['Content-Type'] = 'application/json'

        # Do basic update validation
        user = get_user_for_update(self.request, self.response)
        if user == None:
            return

        write_response(self.response, "0", json.dumps(user.to_dict()))
        return 

class VerifyUserHandler(webapp.RequestHandler):
    def get(self, verification):
        self.response.headers['Content-Type'] = 'text/plain'
        logging.debug("In VerifyUserHandler")

        # Only want one user, but COULD get multiple.  Verify 'em all!
        users = GameUser.get_by_verification(verification)
        if users.count() == 0:
            self.response.write("Invalid verification URL.  Please contact support.")
        elif users.count > 1:
            logging.warning("Multiple users with verification code: %s" % verification)

        for user in users:
            user.status = USER_VERIFIED
            user.put()

        self.response.out.write("Verified!")

class CreateUserHandler(webapp.RequestHandler):
    """  Creates a user for this game
    
    Input:
          fields         : gameid, name, password, email
          optional fields: phone, blob

          example: /user/create?password=aPassword&name=aUserName&gameid=j18dx2ll8

    Output:
          None

          example: {'data': {}, 'status': 0}

    Error Statuses:
          1: Required input fields are missing
          2: User name already exists
          4: Gameid is invalid
          13: Email address already exists
          """

    def get(self):
        if GET_ENABLED:
            return self.post()
        else:
            write_response(self.response, "10", None, "GET not enabled")

    @validate_inputs(required=['name', 'password', 'gameid'])
    def post(self):
        logging.debug("In CreateUserHandler")
        self.response.headers['Content-Type'] = 'application/json'

        # Verify the gameid is valid:
        gameid = self.request.get('gameid')
        if gameid not in GAMES:
            write_response(self.response, "4", None, "gameid is invalid: %s" % gameid)
            return

        # Verify that this user name is unique
        name = self.request.get('name')
        game = GAMES[gameid]['name']
        logging.debug("Email is: " + self.request.get('email'))
        if not GameUser.name_is_available(name, game):
            write_response(self.response, "2", None, 
                           "User name %s already exists for this game." % name)
            return
           
        # Verify that this email is unique
        if GAMES[gameid]['emailVerification']:
            email = self.request.get('email')
            if email == None or email == '':
                write_response(self.response, "1", None, 
                               "Required fields are missing: %s." % email)

            game = GAMES[gameid]['name']
            email = encrypt(email.lower())
            if not GameUser.email_is_available(email, game):
                write_response(self.response, "13", None, 
                               "Email address %s already exists for this game." % email)
                return
        else:
            email = encrypt(self.request.get('email').lower())
            
        user = GameUser()
        user.password, user.salt = saltedhash_hex(self.request.get('password'))
        user.name = name.lower()
        user.game = game
        logging.debug("Email NOW is: " + email)
        user.email = email
        user.phone = encrypt(self.request.get('phone'))
        user.blob = self.request.get('blob')

        # Perform email verification for those games that require it.
        # Otherwise, just mark the user as verified.

        if GAMES[gameid]['emailVerification']:
            user.status = USER_UNVERIFIED
            send_email(user, GAMES[gameid]['name'])
        else:
            user.status = USER_VERIFIED

        user.put()
        write_response(self.response, "0", {})


class UpdateItemHandler(webapp.RequestHandler):
    """  Updates a user item
    
    Input:
          fields: gameid, name, token, itemtype, itemname, quantity, blob

          example: /item/update?token=41c4ba287d0332e&gameid=j18dx2ll8&itemtype=metal&name=aUserName&itemname=silver&quantity=4

    Output:
          None

          example: {'data': {}, 'status': 0}

    Error Statuses:
          1: Required input fields are missing
          4: Gameid is invalid
          6: User does not exist
          9: Quantity must be an integer
          """

    def get(self):
        if GET_ENABLED:
            return self.post()
        else:
            write_response(self.response, "10", None, "GET not enabled")

    @validate_inputs(required=['token', 'name', 'gameid', 'itemtype', 'itemname', 'quantity'])
    def post(self):
        """ Just updates the item quantity """
        logging.debug("In UpdateItemHandler")
        self.response.headers['Content-Type'] = 'application/json'

        # Do basic update validation
        user = get_user_for_update(self.request, self.response)
        if user == None:
            return

        # Get User Item
        itemtype = self.request.get('itemtype')
        name = self.request.get('itemname')
        item = GameItem.get(user, itemtype, name)

        if item == None:
            write_response(self.response, "12", None, "Item type %s with name %s does not exist for user %s." % (itemtype, name, self.request.get('name')))
            return

        try:
            item.quantity = int(self.request.get('quantity'))
        except ValueError:
            write_response(self.response, "9", None, 
                           "quantity %s must be an integer" % self.request.get('quantity'))
            return None

        item.blob = self.request.get('blob')
        item.put()
        write_response(self.response, "0", {})


class DeleteItemHandler(webapp.RequestHandler):
    """  Removes an item from a user.
    
    Input:
          fields: gameid, token, name, itemtype, itemname

          example: /item/delete?token=e13f697140634d14&gameid=j18dx2ll8&itemname=silver&itemtype=metal&name=aUserName

    Output:
          None

          example: {'data': {}, 'status': 0}

    Error Statuses:
          1: Required input fields are missing
          4: Gameid is invalid
          6: User does not exist
          12: Item does not exist
          """

    def get(self):
        if GET_ENABLED:
            return self.post()
        else:
            write_response(self.response, "10", None, "GET not enabled")

    @validate_inputs(required=['token', 'name', 'gameid', 'itemtype', 'itemname'])
    def post(self):
        """ Removes an item from a user """
        logging.debug("In DeleteItemHandler")
        self.response.headers['Content-Type'] = 'application/json'

        # Do basic update validation
        user = get_user_for_update(self.request, self.response)
        if user == None:
            return

        # Get User Item
        itemtype = self.request.get('itemtype')
        name = self.request.get('itemname')
        item = GameItem.get(user, itemtype, name)

        if item == None:
            write_response(self.response, "12", None, "Item type %s with name %s does not exist for user %s." % (itemtype, name, self.request.get('name')))
            return

        item.delete()
        write_response(self.response, "0", {})


class GetItemHandler(webapp.RequestHandler):
    """  Gets a user item.  
    
    Input:
          fields: gameid, token, name, itemtype, itemname

          example: /item/get?token= 41c4ba287d0332e&gameid=j18dx2ll8&itemname=silver&itemtype=metal&name=aUserName

    Output:
          Item dictionary

          example: {'data': {'itemtype': 'metal', 
                             'name': 'silver', 
                             'blob': 'asdf1234', 
                             'quantity': 4},
                    'status': 0}

    Error Statuses:
          1: Required input fields are missing
          4: Gameid is invalid
          6: User does not exist
          12: Item does not exist
       
    """


    def get(self):
        if GET_ENABLED:
            return self.post()
        else:
            write_response(self.response, "10", None, "GET not enabled")

    @validate_inputs(required=['token', 'name', 'gameid', 'itemtype', 'itemname'])
    def post(self):
        """ Removes an item from a user """
        logging.debug("In GetItemHandler")
        self.response.headers['Content-Type'] = 'application/json'

        # Do basic update validation
        user = get_user_for_update(self.request, self.response)
        if user == None:
            return

        # Get User Item
        itemtype = self.request.get('itemtype')
        name = self.request.get('itemname')
        item = GameItem.get(user, itemtype, name)
        if item == None:
            write_response(self.response, "12", None, "Item type %s with name %s does not exist for user %s." % (itemtype, name, self.request.get('name')))
        else:
            write_response(self.response, "0", json.dumps(item.to_dict()))
        return 


class AddItemHandler(webapp.RequestHandler):
    """  Adds an item to a user.
    
    Input:
          fields: gameid, token, name, itemtype, itemname, quantity, blob

          example: /item/add?token=e13f697140634d14&gameid=j18dx2ll8&itemtype=metal&name=aUserName&itemname=silver&quantity=3 

    Output:
          None

          example: {'data': {}, 'status': 0}

    Error Statuses:
          1: Required input fields are missing
          4: Gameid is invalid
          6: User does not exist
          9: Quantity must be an integer
          11: Item type and name already exist for this user
          """


    def get(self):
        if GET_ENABLED:
            return self.post()
        else:
            write_response(self.response, "10", None, "GET not enabled")

    @validate_inputs(required=['token', 'name', 'gameid', 'itemtype', 'itemname', 'quantity'])
    def post(self):
        logging.debug("In AddItemHandler")
        self.response.headers['Content-Type'] = 'application/json'

        # Do basic update validation
        user = get_user_for_update(self.request, self.response)
        if user == None:
            return

        # Ensure this item does not already exist for this user
        itemtype = self.request.get('itemtype')
        name = self.request.get('itemname')
        item = GameItem.get(user, itemtype, name)
        if item != None:
            write_response(self.response, "11", None, 
                           "Item with name %s and type %s already exists for user %s" %
                           (name, itemtype, user.name))
            return

        # Add item to user
        item = GameItem()
        item.itemtype = itemtype
        item.name = name
        item.user = user
        item.blob = self.request.get('blob')
        try:
            item.quantity = int(self.request.get('quantity'))
        except ValueError:
            write_response(self.response, "9", None, 
                           "quantity %s must be an integer" % self.request.get('quantity'))
            return None

        item.put()
        write_response(self.response, "0", {})


class ListItemHandler(webapp.RequestHandler):
    """  Lists all the items for a user
    
    Input:
          fields: gameid, token, name

          example: /item/list?token=59998d5dc2e88f45&gameid=j18dx2ll8&name=aUserName

    Output:
          List of item dictionaries

          example: {'data': [{'itemtype': 'metal', 
                              'name': 'silver', 
                              'blob': 'asdf1234', 
                              'quantity': 3},
                             {'itemtype': 'metal', 
                              'name': 'copper', 
                              'blob': 'asdf1234', 
                              'quantity': 3}],
                    'status': 0}

    Error Statuses:
          1: Required input fields are missing
          4: Gameid is invalid
          6: User does not exist
          """


    def get(self):
        if GET_ENABLED:
            return self.post()
        else:
            write_response(self.response, "10", None, "GET not enabled")

    @validate_inputs(required=['token', 'name', 'gameid'])
    def post(self):
        logging.debug("In AddItemHandler")
        self.response.headers['Content-Type'] = 'application/json'

        # Do basic update validation
        user = get_user_for_update(self.request, self.response)
        if user == None:
            return

        itemlist = []
        items = GameItem.list(user)
        for item in items:
            itemdict = item.to_dict()
            itemlist.append(itemdict)

        write_response(self.response, "0", json.dumps(itemlist))


def get_user_for_update(request, response):
    """ Utility function that does a bunch of the input validation required
    for services that update user information."""
    # Verify the gameid is valid:
    gameid = request.get('gameid')
    if gameid not in GAMES:
        write_response(response, "4", None, "Gameid is invalid: %s" % gameid)
        return None

    # Get the user
    name = request.get('name')
    game = GAMES[gameid]['name']
    user = GameUser.get_by_name(name, game)
    if not user:
        write_response(response, "6", None, 
                       "User %s does not exist" % name)
        return None

    # Ensure token is still valid
    token = request.get('token')
    if token != user.token:
        logging.error(token + " != " + user.token)
        write_response(response, "7", None, "Token %s is invalid" % token)
        return None

    exp_date = user.last_login_date + timedelta(seconds=user.expiration) 
    if exp_date < datetime.now():
        write_response(response, "8", None, "Token has expired.  Log in again.")
        return None

    return user

def send_email(user, game_name):
    """ Send verification email to user """
    random_path = ''.join(random.choice(string.letters + string.digits) for i in xrange(24))
    message = mail.EmailMessage(sender="%s Verifier < verify@yaauthservice.appspotmail.com>" % game_name,
                                subject="Your account needs to be verified")

    message.to = decrypt(user.email)
    message.body = "Welcome to %s.  Please click the following link to complete the sign-up process.\n" % game_name
    message.body += "\n"
    message.body += "https://yaauthservice.appspot.com/user/verify/" + random_path
    message.send()
    user.verification = random_path

"""
def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([('/item/add', AddItemHandler),
                                          ('/item/update', UpdateItemHandler),
                                          ('/item/delete', DeleteItemHandler),
                                          ('/item/get', GetItemHandler),
                                          ('/item/list', ListItemHandler),
                                          ('/user/create', CreateUserHandler),
                                          ('/user/get', GetUserHandler),
                                          ('/user/delete', DeleteUserHandler),
                                          ('/user/list', ListUserHandler),
                                          ('/user/login', LoginHandler),
                                          ('/user/verify/([^/]+)', VerifyUserHandler),
                                          ('/user/update', UpdateUserHandler)],
                                         debug=True)

    run_wsgi_app(application)

if __name__ == "__main__":
    main()
"""

logging.getLogger().setLevel(logging.DEBUG)
app = webapp.WSGIApplication([('/item/add', AddItemHandler),
                              ('/item/update', UpdateItemHandler),
                              ('/item/delete', DeleteItemHandler),
                              ('/item/get', GetItemHandler),
                              ('/item/list', ListItemHandler),
                              ('/user/create', CreateUserHandler),
                              ('/user/get', GetUserHandler),
                              ('/user/delete', DeleteUserHandler),
                              ('/user/list', ListUserHandler),
                              ('/user/login', LoginHandler),
                              ('/user/verify/([^/]+)', VerifyUserHandler),
                              ('/user/update', UpdateUserHandler)],
                               debug=True)

