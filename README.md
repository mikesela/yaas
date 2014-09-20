Overview:

  This is an auth and item server for an online game. It provides APIs enabling a game to register and manage servers and then add inventory to game users.

  Here is the list of supported APIs:
      /user/create
      /user/login
      /user/list
      /user/delete
      /user/update
      /user/get

      /item/add
      /item/update
      /item/delete
      /item/get
      /item/list

  Each API should be called via an HTTP 'POST' using HTTPS.  All APIs live 
  on this host: yaauthservice.appspot.com

  All returned data comes back in the form of a JSON dictionary.  These 
  dictionaries will always contain a 'status' key at the top level.  If a 
  'status' of 0 is returned, that means the API was successful and that returned
  data can be found (if any is needed) attached to the 'data' key.

  If, however, a non-zero 'status' value is returned, then there will be no
  data and instead an error message will be returned, attached to the 'message'
  key.



API: /user/login
    Logs a user in and returns a time-limited token which is a required input
    for other APIs.  If caller does not specify an expiration time, the 
    token will be generated with the default expiration.  If the gameid for
    this user is configured to require email verification, the user will
    not be able to login until the verification link in the email has been
    clicked.
    
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



API: /user/list
    Lists all the users for this game.
    
    Input:
          fields: gameid

          example: /user/list?gameid=j18dx2ll8

    Output:
          List of user dictionaries

          example: {'data': [{'create_date': '2011-10-02 17:36:13.532114',
                              'credits': 0,
                              'email': '',
                              'blob': '',
                              'experience': 0,
                              'game': 'testgame',
                              'last_login_date': '2011-10-04 00:35:15.528540',
                              'level': 0,
                              'losses': 0,
                              'modify_date': '2011-10-02 22:31:40.068998',
                              'name': 'Mikes1',
                              'phone': '415-123-4568',
                              'wins': 0},
                             {'create_date': '2011-10-10 02:17:47.514796',
                              'credits': 0,
                              'email': '',
                              'experience': 0,
                              'game': 'testgame',
                              'last_login_date': '2011-10-10 02:17:47.514876',
                              'level': 0,
                              'blob': 0,
                              'losses': 0,
                              'modify_date': '2011-10-10 02:17:47.514812',
                              'name': 'aUserName',
                              'phone': '',
                              'wins': 0}],
                   'status': 0}

    Error Statuses:
          1: Required input fields are missing
          4: Gameid is invalid



API: /user/delete
    Deletes a user for this game.
    
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



API: /user/update
    Updates a user
    
    Input:
          fields: gameid, name, token
          optional fields: email, phone, wins, losses, credits, level, experience

          example: /user/update?gameid=j18dx2ll8&name=aUserName&credits=3&wins=1&losses=2&experience=5&phone=(123)456-7890&token=1c40d1991684f1dd&level=4&email=testing@email.com&blob=thisIsABlob

    Output:
          None

          example: {'data': {}, 'status': 0}

    Error Statuses:
          1: Required input fields are missing
          4: Gameid is invalid
          6: User does not exist
          7: Token is invalid
          8: Token has expired



API: /user/get
    Lists all the users for this game.
    
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
                             'blob': 'thisIsABlob',
                             'last_login_date': '2011-10-10 02:17:54.512005',
                             'level': 4,
                             'losses': 2,
                             'modify_date': '2011-10-10 02:17:54.558967',
                             'name': 'aUserName',
                             'phone': '(123)456-7890',
                             'wins': 1},
                   'status': 0}

    Error Statuses:
          1: Required input fields are missing
          4: Gameid is invalid
          6: User does not exist



API: /user/create
    Creates a user for this game.  If the gameid is configured in the system
    to require email verification, then the user will be emailed with a 
    verification link.
    
    Input:
          fields: gameid, name, password

          example: /user/create?password=aPassword&name=aUserName&gameid=j18dx2ll8

    Output:
          None

          example: {'data': {}, 'status': 0}

    Error Statuses:
          1: Required input fields are missing
          4: Gameid is invalid
          2: User name already exists



API:  /item/update
    Updates the quantity of a user item
    
    Input:
          fields: gameid, name, token, itemtype, itemname, quantity

          example: /item/update?token=41c4ba287d0332e&gameid=j18dx2ll8&itemtype=metal&name=aUserName&itemname=silver&quantity=4&blob=thisIsAlsoABlob

    Output:
          None

          example: {'data': {}, 'status': 0}

    Error Statuses:
          1: Required input fields are missing
          4: Gameid is invalid
          6: User does not exist
          9: Quantity must be an integer



API: /item/delete
    Removes an item from a user.
    
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



API:  /item/get
    Gets a user item.  Item quantity is the only thing of interest
    
    Input:
          fields: gameid, token, name, itemtype, itemname

          example: /item/get?token= 41c4ba287d0332e&gameid=j18dx2ll8&itemname=silver&itemtype=metal&name=aUserName

    Output:
          Item dictionary

          example: {'data': {'itemtype': 'metal', 
                             'name': 'silver', 
                             'blob': 'thisIsAlsoABlob', 
                             'quantity': 4},
                    'status': 0}

    Error Statuses:
          1: Required input fields are missing
          4: Gameid is invalid
          6: User does not exist
          12: Item does not exist



API: /item/add
    Adds an item to a user.
    
    Input:
          fields         : gameid, token, name, itemtype, itemname, quantity, 
          optional fields: blob

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



API: /item/list
    Lists all the items for a user
    
    Input:
          fields: gameid, token, name

          example: /item/list?token=59998d5dc2e88f45&gameid=j18dx2ll8&name=aUserName

    Output:
          List of item dictionaries

          example: {'data': [{'itemtype': 'metal', 
                              'name': 'silver', 
                              'quantity': 3},
                             {'itemtype': 'metal', 
                              'name': 'copper', 
                              'blob': 'thisItemHasABlob', 
                              'quantity': 3}],
                    'status': 0}

    Error Statuses:
          1: Required input fields are missing
          4: Gameid is invalid
          6: User does not exist
