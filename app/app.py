import os
from flask import Flask, redirect, url_for, session, render_template_string, request
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client.errors import OAuthError
from dotenv import load_dotenv
from authlib.common.security import generate_token

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "2tKBGXHD9rjlJQvV1Z7ukCkDeyOjWvF7")

# Регистрация клиента OAuth
oauth = OAuth(app)
oauth.register(
    name="keycloak",
    client_id=os.getenv("KEYCLOAK_CLIENT_ID"),
    client_secret=os.getenv("KEYCLOAK_CLIENT_SECRET"),
    server_metadata_url=os.getenv("KEYCLOAK_METADATA_URL"),
    client_kwargs={
        "scope": "openid profile email",
        "prompt": "login"  # force login prompt every time
    },
)

@app.route("/")
def index():
    user = session.get("user")
    if user:
        return render_template_string('''
            <h1>Welcome, {{ user['name'] }}!</h1>
            <form action="{{ url_for('logout') }}" method="post">
                <button type="submit">Logout</button>
            </form>
        ''', user=user)
    else:
        return render_template_string('''
            <h1>Hello, you are not logged in.</h1>
            <form action="{{ url_for('login') }}" method="get">
                <button type="submit">Login</button>
            </form>
        ''')

# Страница входа
@app.route("/login", methods=["GET"])
def login():
    session.clear()
    nonce = generate_token()
    redirect_uri = url_for("auth", _external=True)
    return oauth.keycloak.authorize_redirect(redirect_uri, nonce=nonce)

# Обработка авторизации
@app.route("/auth")
def auth():
    try:
        print("auth")
        token = oauth.keycloak.authorize_access_token()
        nonce = session.pop("nonce", None)
        user = oauth.keycloak.parse_id_token(token, nonce=nonce)
        session["user"] = user
        return redirect("/")
    except OAuthError as e:
        return f"<h1>Authentication failed</h1><p>{e.error}: {e.description}</p>", 400
    except Exception as e:
        return f"<h1>Unexpected error</h1><p>{str(e)}</p>", 500


# Страница выхода
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    logout_url = f"{os.getenv('KEYCLOAK_LOGOUT_URL')}?redirect_uri={url_for('index', _external=True)}"
    return redirect(logout_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
