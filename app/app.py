from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import secrets

app = Flask(__name__)
app.secret_key = 'HtEKcqNFCMGE1QjT1MCjIic0QyZtFKnk'

oauth = OAuth(app)
oauth.register(
    name='keycloak',
    client_id='my-flask-app',
    client_secret='HtEKcqNFCMGE1QjT1MCjIic0QyZtFKnk',
    server_metadata_url='http://localhost:8080/realms/master/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid profile email',
    }
)

@app.route('/')
def homepage():
    user = session.get('user')
    return f'Hello, {user["preferred_username"]}' if user else 'Not logged in'

@app.route('/login')
def login():
    redirect_uri = url_for('callback', _external=True)
    return oauth.keycloak.authorize_redirect(
        redirect_uri=redirect_uri,
        prompt='login'  # <-- это важно
    )

@app.route('/callback')
def callback():
    token = oauth.keycloak.authorize_access_token()
    nonce = session.pop('nonce', None)
    if nonce is None:
        return "Missing nonce in session", 400

    # ❗ ВАЖНО: передаём nonce в parse_id_token()
    user = oauth.keycloak.parse_id_token(token, nonce=nonce)
    session['user'] = user
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
