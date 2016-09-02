from flask_login import LoginManager, UserMixin
from flask import Request
import ast
import os
from itsdangerous import URLSafeTimedSerializer

from authorizers import FileAuthorizer
from authenticators import FileAuthenticator

'''
References:
    * https://flask-login.readthedocs.io/en/latest/
    * http://thecircuitnerd.com/flask-login-tokens/
    * http://flask-security.readthedocs.io/en/latest/features.html
'''

# secret key used for the session user cookie
COOKIE_SECRET_KEY = os.environ['COOKIE_SECRET_KEY']
SESSION_TIMEOUT_SECONDS = int(os.getenv('SESSION_TIMEOUT_SECONDS', 120))

REMEMBER_COOKIE_DOMAIN = os.getenv('SESSION_ID_DOMAIN', None) # used by flask-login

login_manager = LoginManager()
login_manager.session_protection = 'strong'

#Login_serializer used to encryt and decrypt the cookie token for the remember me option of flask-login
login_serializer = URLSafeTimedSerializer(COOKIE_SECRET_KEY)

class SessionUser(UserMixin):
    actas = ''
    def __init__(self, username, userpasshash):
        ''' Note that the userpasshash can be some kind of a token too.'''
        self.user_id = username
        self.userpasshash = userpasshash

    def get_auth_token(self):
        ''' Encode a secure token for cookie. This is used to remember the user. '''
        return login_serializer.dumps(self.user_id, self.userpasshash)

    def get_id(self):
        return self.user_id

    def get_username(self):
        return self.user_id

    def get_actas(self):
        print 'actas: ', self.actas
        return self.actas

    @staticmethod
    def get(user_id):
        '''
        Static method do determine if user_id is valid.
        Returns a SessionUser object if valid and None if not (as required be Flask-Login).
        '''
        if FileAuthorizer().instance.is_user_valid(user_id):
            userpasshash = FileAuthenticator().instance.get_hash(user_id)
            if userpasshash:
                return SessionUser(user_id, userpasshash)
        return None

@login_manager.user_loader
def load_user(user_id):
    '''
    This callback is used to reload the user object from the user ID stored in the session.
    It should take the unicode ID of a user, and return the corresponding user object.
    '''
    return SessionUser.get(user_id)

@login_manager.token_loader
def load_token(token):
    '''
    Flask-Login token_loader callback.
    The token_loader function asks this function to take the token that was
    stored on the users computer process it to check if its valid and then
    return a User Object if its valid or None if its not valid.
    '''
    #The Token itself was generated by User.get_auth_token (see above).
    #Decrypt the Security Token, data = [username, hashpass]
    data = login_serializer.loads(token, max_age=SESSION_TIMEOUT_SECONDS)
    #Find the User
    user = SessionUser.get(data[0])
    #Check userpasshash and return user or None
    if user and data[1] == user.userpasshash:
        return user
    return None
