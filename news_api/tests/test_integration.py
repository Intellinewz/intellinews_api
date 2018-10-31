import json

token = ''


""" Auth Tests for reg and login- api/v1/auth/login/
and api/v1/auth/register/ """


def test_registration(testapp):
    """ Tests new user registration returns a 201 status code
    """
    account = {
        'email': 'test@example.com',
        'password': 'hello',
    }

    response = testapp.post('/api/v1/auth/register/', json.dumps(account))
    global token
    token = response.json['token']
    assert response.status_code == 201
    assert response.json['token']


def test_invalid_registration(testapp):
    """ Tests invalid registration returns 400 status code
    """
    account = {
        'email': 'test_two@example.com',
    }

    response = testapp.post('/api/v1/auth/register/', json.dumps(account), status='4**')
    assert response.status_code == 400


def test_good_login(testapp):
    """ Tests login route returns 201 status code
    """
    account = {
        'email': 'test@example.com',
        'password': 'hello',
    }

    response = testapp.post('/api/v1/auth/login/', json.dumps(account))
    assert response.status_code == 201
    assert response.json['token']


# """ Looks for password and doen't find one"""
# def test_bad_login(testapp):
#     """ Tests bad login returns 400
#     """
#     account = {
#         'email': '{test@example.com}',
#     }

#     response = testapp.post('/api/v1/auth/login/', json.dumps(account))
#     assert response == KeyError('password')
#     # assert response.json['token']


""" Preferences Tests- api/v1/preferences/"""


def test_preferences_post_auth(testapp):
    """ Tests authenticated user posting new prefs
    """
    preference_order = {
        'preference_order': ["anger", "joy"],
        }
    global token
    testapp.authorization = ('Bearer', token)
    response = testapp.post('/api/v1/preferences/', json.dumps(preference_order))
    assert response.status_code == 201


def test_preferences_post_not_auth(testapp):
    """ Test cannot post preferences without auth
    """
    preference_order = {
        'preference_order': ["anger", "joy"],
    }
    testapp.authorization = None
    response = testapp.post('/api/v1/preferences/', json.dumps(preference_order), status=403)
    print(response)
    assert response.status_code == 403



def test_invalid_preferences_lookup_methods(testapp):
    """ Tests that user can't do put or delete to preferences lookup route
    """
    global token
    testapp.authorization = ('Bearer', token)
    response = testapp.put('/api/v1/preferences/', status='4**')
    assert response.status_code == 405
    response = testapp.delete('/api/v1/preferences/', status='4**')
    assert response.status_code == 405
    response = testapp.post('/api/v1/preferences/', status='4**')
    assert response.status_code == 400


""" Feed tests- api/v1/feed """


def test_get_feed_auth(testapp):
    """ Tests authorized user can get feed, make sure response has
    something particular on it
    """
    global token
    testapp.authorization = ('Bearer', token)
    response = testapp.get('/api/v1/feed/')
    assert response.status_code == 200


def test_get_feed_not_auth(testapp):
    """ Tests unauthorized user cannot get feed
    """
    testapp.authorization = None
    response = testapp.get('/api/v1/feed/', status='4**')
    assert response.status_code == 403


def test_invalid_feed_lookup_methods(testapp):
    """ Tests you cannot delete or post to the feed
    """
    global token
    testapp.authorization = ('Bearer', token)
    response = testapp.put('/api/v1/feed/', status='4**')
    assert response.status_code == 405
    response = testapp.delete('/api/v1/feed/', status='4**')
    assert response.status_code == 405
    response = testapp.post('/api/v1/feed/', status='4**')
    assert response.status_code == 405


""" Visuals tests- api/v1/visuals """


def test_get_visuals_returns_not_found_when_db_empty(testapp, test_entry):
    """ Tests visuals route returns a not found code when there's nothing in the archives table
    """
    # global token
    # testapp.authorization = ('Bearer', token)
    testapp.authorization = None
    response = testapp.get('/api/v1/visuals/', status='4**')
    assert response.status_code == 404
