import httplib2, urllib, httplib
import json
import yaml
import sys
import pprint
import time

#HOST = 'localhost:8080'
HOST = 'yaauthservice.appspot.com'
#GAMEID = 'j18dx2ll8'
GAMEID = 'testgame'
NAME = '__aTestUser__ blah blah'
PASSWORD = 'aPassword'


#
# Utility functions
#
def post(path, indict):
    tuples = zip(indict.keys(), indict.values())
    print path
    print path + "?" + "&".join([key + "=" + str(value) for (key, value) in tuples])
    pprint.pprint(indict)
    params = urllib.urlencode(indict)
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    if HOST.startswith('localhost'):
        conn = httplib.HTTPConnection(HOST)
    else:
        conn = httplib.HTTPSConnection(HOST)
    conn.request("POST", path, params, headers)
    response = conn.getresponse()
    status = response.status
    print 'Status is', status
    readdata = response.read()
    print 'Data is', readdata
    data = json.loads(readdata)
    pprint.pprint(data)
    print
    return status, data

def item_list(name, token, gameid):
    path = '/item/list'
    dicty = dict(name=name, gameid=gameid, token=token)
    httpstatus, apiresponse = post(path, dicty)
    assert httpstatus == 200
    return apiresponse

def item_get(name, token, gameid, itemtype, itemname):
    path = '/item/get'
    dicty = dict(name=name, gameid=gameid, token=token, itemtype=itemtype,
                 itemname=itemname)
    httpstatus, apiresponse = post(path, dicty)
    assert httpstatus == 200
    return apiresponse

def item_delete(name, token, gameid, itemtype, itemname):
    path = '/item/delete'
    dicty = dict(name=name, gameid=gameid, token=token, itemtype=itemtype,
                 itemname=itemname)
    httpstatus, apiresponse = post(path, dicty)
    assert httpstatus == 200
    return apiresponse

def item_update(name, token, gameid, itemtype, itemname, itemqty, blob=None):
    path = '/item/update'
    dicty = dict(name=name, gameid=gameid, token=token, itemtype=itemtype,
                 itemname=itemname, quantity=itemqty)
    if blob:
        dicty['blob']=blob
    httpstatus, apiresponse = post(path, dicty)
    assert httpstatus == 200
    return apiresponse

def item_add(name, token, gameid, itemtype, itemname, itemquantity, blob=None):
    path = '/item/add'
    dicty = dict(name=name, gameid=gameid, token=token, itemtype=itemtype,
                 itemname=itemname, quantity=itemquantity)
    if blob:
        dicty['blob']=blob
    httpstatus, apiresponse = post(path, dicty)
    assert httpstatus == 200
    return apiresponse

def user_delete(name, gameid):
    path = '/user/delete'
    dicty = dict(name=name, gameid=gameid)
    httpstatus, apiresponse = post(path, dicty)
    assert httpstatus == 200
    return apiresponse

def user_create(name, password, gameid):
    path = '/user/create'
    dicty = dict(name=name, gameid=gameid, password=password)
    httpstatus, apiresponse = post(path, dicty)
    assert httpstatus == 200
    #assert apiresponse['status'] == 0
    return apiresponse

def user_update(name, token, gameid, email=None, phone=None, wins=None,
                losses=None, credits=None, level=None, experience=None, 
                blob=None):
    path = '/user/update'
    dicty = dict(name=name, gameid=gameid, token=token)
    if email:
        dicty['email'] = email
    if phone:
        dicty['phone'] = phone
    if wins:
        dicty['wins'] = wins
    if losses:
        dicty['losses'] = losses
    if credits:
        dicty['credits'] = credits
    if level:
        dicty['level'] = level
    if experience:
        dicty['experience'] = experience
    if blob:
        dicty['blob'] = blob

    httpstatus, apiresponse = post(path, dicty)
    assert httpstatus == 200
    #assert apiresponse['status'] == 0
    return apiresponse

def user_login(name, password, gameid, expiration=None):
    path = '/user/login'
    dicty = dict(name=name, gameid=gameid, password=password)
    if expiration != None:
        dicty['expiration'] = expiration
    httpstatus, apiresponse = post(path, dicty)
    assert httpstatus == 200
    #assert apiresponse['status'] == 0
    #return apiresponse['data']['token']
    return apiresponse

def user_get(name, token, gameid):
    path = '/user/get'
    dicty = dict(name=name, gameid=gameid, token=token)
    httpstatus, apiresponse = post(path, dicty)
    assert httpstatus == 200
    #assert apiresponse['status'] == 0
    #return apiresponse['data']
    return apiresponse

def user_list(gameid):
    path = '/user/list'
    dicty = dict(gameid=gameid)
    httpstatus, apiresponse = post(path, dicty)
    assert httpstatus == 200
    return apiresponse
#
# Test cases
#
def test_create_user_success():
    user_delete(NAME, GAMEID)
    resp = user_create(NAME, PASSWORD, GAMEID)
    assert resp['status'] == 0
    user_delete(NAME, GAMEID)

def test_list_user_success():
    user_delete(NAME, GAMEID)
    user_delete(NAME + '2', GAMEID)
    user_create(NAME, PASSWORD, GAMEID)
    user_create(NAME + '2', PASSWORD, GAMEID)
    resp = user_list(GAMEID)
    assert resp['status'] == 0
    users = resp['data']
    assert len(users) >= 2
    user_delete(NAME, GAMEID)
    user_delete(NAME + '2', GAMEID)

def test_login_success():
    user_delete(NAME, GAMEID)
    resp = user_create(NAME, PASSWORD, GAMEID)
    token = user_login(NAME, PASSWORD, GAMEID)['data']['token']
    assert token != None and token != ''
    user_delete(NAME, GAMEID)

def test_login_success_with_expiration():
    user_delete(NAME, GAMEID)
    resp = user_create(NAME, PASSWORD, GAMEID)
    token = user_login(NAME, PASSWORD, GAMEID, expiration=5)['data']['token']
    assert token != None and token != ''
    user_delete(NAME, GAMEID)

def test_login_success_token_expires():
    user_delete(NAME, GAMEID)
    resp = user_create(NAME, PASSWORD, GAMEID)
    token = user_login(NAME, PASSWORD, GAMEID, expiration=2)['data']['token']
    time.sleep(5)
    itemtype = 'metal'
    itemname = 'silver'
    itemqty = 3
    resp = item_add(NAME, token, GAMEID, itemtype, itemname, itemqty)
    assert resp['status'] != 0
    user_delete(NAME, GAMEID)

def test_login_failure_invalid_password():
    user_delete(NAME, GAMEID)
    user_create(NAME, PASSWORD, GAMEID)
    resp = user_login(NAME, PASSWORD + 'x', GAMEID)
    assert resp['status'] != 0
    gotKeyError = False
    try:
        token = resp['data']['token']
    except KeyError:
        gotKeyError = True
    assert gotKeyError
    user_delete(NAME, GAMEID)

def test_login_failure_invalid_user():
    user_delete(NAME, GAMEID)
    user_create(NAME, PASSWORD, GAMEID)
    resp = user_login(NAME + 'x', PASSWORD, GAMEID)
    assert resp['status'] != 0
    gotKeyError = False
    try:
        token = resp['data']['token']
    except KeyError:
        gotKeyError = True
    assert gotKeyError
    user_delete(NAME, GAMEID)


def test_create_user_fail_dup():
    user_delete(NAME, GAMEID)
    resp = user_create(NAME, PASSWORD, GAMEID)
    resp = user_create(NAME, PASSWORD, GAMEID)
    assert resp['status'] != 0
    user_delete(NAME, GAMEID)
    

def test_update_user_success():
    user_delete(NAME, GAMEID)
    resp = user_create(NAME, PASSWORD, GAMEID)
    token = user_login(NAME, PASSWORD, GAMEID)['data']['token']
    email = 'testing@email.com'
    phone = '(123)456-7890'
    wins = 1
    blob = 'this is one hell of a blob'
    losses = 2
    credits = 3
    level = 4
    experience = 5

    resp = user_update(NAME, token, GAMEID, email=email, phone=phone, wins=wins,
                       losses=losses,credits=credits,level=level,
                       experience=experience, blob=blob)
    assert resp['status'] == 0
    user = user_get(NAME, token, GAMEID)['data']
    assert email == user['email']
    assert phone == user['phone']
    assert wins  == user['wins']
    assert losses == user['losses']
    assert credits == user['credits']
    assert experience == user['experience']
    assert level == user['level']
    assert blob == user['blob']
    user_delete(NAME, GAMEID)


def test_update_min_user_success():
    user_delete(NAME, GAMEID)
    resp = user_create(NAME, PASSWORD, GAMEID)
    token = user_login(NAME, PASSWORD, GAMEID)['data']['token']
    email = ''
    phone = ''

    resp = user_update(NAME, token, GAMEID, email=email, phone=phone)
    assert resp['status'] == 0
    user = user_get(NAME, token, GAMEID)['data']
    assert email == user['email']
    assert phone == user['phone']
    user_delete(NAME, GAMEID)


def test_update_user_failure_invalid_user():
    user_delete(NAME, GAMEID)
    resp = user_create(NAME, PASSWORD, GAMEID)
    token = user_login(NAME, PASSWORD, GAMEID)['data']['token']
    resp = user_update(NAME + 'x', token, GAMEID)
    assert resp['status'] != 0
    user_delete(NAME, GAMEID)


def test_add_item_success():
    user_delete(NAME, GAMEID)
    resp = user_create(NAME, PASSWORD, GAMEID)
    token = user_login(NAME, PASSWORD, GAMEID)['data']['token']
    itemtype = 'metal'
    itemname = 'silver'
    itemqty = 3
    blob = 'thisIsABlob'
    resp = item_add(NAME, token, GAMEID, itemtype, itemname, itemqty, blob=blob)
    assert resp['status'] == 0
    resp = item_get(NAME, token, GAMEID, itemtype, itemname)
    assert resp['status'] == 0
    assert resp['data']['quantity'] == itemqty
    assert resp['data']['blob'] == blob
    item_delete(NAME, token, GAMEID, itemtype, itemname)
    user_delete(NAME, GAMEID)

def test_add_item_fail_invalid_user():
    user_delete(NAME, GAMEID)
    resp = user_create(NAME, PASSWORD, GAMEID)
    token = user_login(NAME, PASSWORD, GAMEID)['data']['token']
    itemtype = 'metal'
    itemname = 'silver'
    itemqty = 3
    resp = item_add(NAME + 'x', token, GAMEID, itemtype, itemname, itemqty)
    user_delete(NAME, GAMEID)
    assert resp['status'] != 0

def test_update_item_success():
    user_delete(NAME, GAMEID)
    resp = user_create(NAME, PASSWORD, GAMEID)
    token = user_login(NAME, PASSWORD, GAMEID)['data']['token']
    itemtype = 'metal'
    itemname = 'silver'
    itemqty = 3
    item_add(NAME, token, GAMEID, itemtype, itemname, itemqty)
    itemqty = 4
    blob = 'this is a blob'
    item_update(NAME, token, GAMEID, itemtype, itemname, itemqty, blob=blob)
    resp = item_get(NAME, token, GAMEID, itemtype, itemname)
    assert resp['status'] == 0
    assert resp['data']['quantity'] == itemqty
    assert resp['data']['blob'] == blob
    item_delete(NAME, token, GAMEID, itemtype, itemname)
    user_delete(NAME, GAMEID)

def test_update_item_fail_no_quantity():
    user_delete(NAME, GAMEID)
    resp = user_create(NAME, PASSWORD, GAMEID)
    token = user_login(NAME, PASSWORD, GAMEID)['data']['token']
    itemtype = 'metal'
    itemname = 'silver'
    itemqty = 3
    item_add(NAME, token, GAMEID, itemtype, itemname, itemqty)
    itemqty = 4
    resp = item_update(NAME, token, GAMEID, itemtype, itemname, None)
    assert resp['status'] != 0
    item_delete(NAME, token, GAMEID, itemtype, itemname)
    user_delete(NAME, GAMEID)

def test_delete_item_success():
    user_delete(NAME, GAMEID)
    resp = user_create(NAME, PASSWORD, GAMEID)
    token = user_login(NAME, PASSWORD, GAMEID)['data']['token']
    itemtype = 'metal'
    itemname = 'silver'
    itemqty = 3
    item_add(NAME, token, GAMEID, itemtype, itemname, itemqty)
    resp = item_delete(NAME, token, GAMEID, itemtype, itemname)
    assert resp['status'] == 0
    resp = item_get(NAME, token, GAMEID, itemtype, itemname)
    assert resp['status'] != 0
    user_delete(NAME, GAMEID)

def test_list_item_success():
    user_delete(NAME, GAMEID)
    resp = user_create(NAME, PASSWORD, GAMEID)
    token = user_login(NAME, PASSWORD, GAMEID)['data']['token']
    itemtype = 'metal'
    itemname = 'silver'
    itemqty = 3
    item_add(NAME, token, GAMEID, itemtype, itemname, itemqty)
    itemname = 'copper'
    item_add(NAME, token, GAMEID, itemtype, itemname, itemqty)
    resp = item_list(NAME, token, GAMEID)
    assert resp['status'] == 0
    itemlist = resp['data']
    assert len(itemlist) == 2
    assert itemlist[0]['name'] == 'silver'
    assert itemlist[1]['name'] == 'copper'
    item_delete(NAME, token, GAMEID, itemtype, 'silver')
    item_delete(NAME, token, GAMEID, itemtype, 'copper')
    user_delete(NAME, GAMEID)
