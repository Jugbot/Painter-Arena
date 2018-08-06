from functools import wraps

from flask import request, g, Response
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth

from app import jwt
from tables import session, User


class SemiAuth(MultiAuth):
    def login_optional(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            selected_auth = None
            if 'Authorization' in request.headers:
                try:
                    scheme, creds = request.headers['Authorization'].split(
                        None, 1)
                except ValueError:
                    # malformed Authorization header
                    pass
                else:
                    for a in self.additional_auth:
                        if a.scheme == scheme:
                            selected_auth = a
                            break
            if selected_auth is None:
                selected_auth = self.main_auth
            g.authorized = True
            res = selected_auth.login_required(f)(*args, **kwargs)
            # Annoyingly, res could be a tuple or Response object
            if (type(res) is tuple and res[1] == 401) \
                    or (type(res) is Response and res.status_code == 401): # If it doesn't let you in, try harder :P
                g.authorized = False
                return f(*args, **kwargs)
            return res
        return decorated

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()
auth = SemiAuth(basic_auth, token_auth)

@basic_auth.verify_password
def verify_password(username, password):
    print("password")
    u = session.query(User).filter_by(username=username).first()
    if not u or not u.verify_password(password):
        return False
    g.user = u
    return True

@token_auth.verify_token
def verify_token(token):
    print("token")
    try:
        data = jwt.loads(token)
    except:  # noqa: E722
        return False
    if 'username' in data:
        g.user = session.query(User).filter_by(username=data['username']).first()
        return bool(g.user)
    return False
