import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, redirect, url_for, session, render_template, render_template_string
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client.errors import OAuthError
from dotenv import load_dotenv
from functools import wraps

# ─── Load environment ──────────────────────────────────────────────────────────
load_dotenv()

# ─── Flask app setup ──────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")

# ─── Logging to file ──────────────────────────────────────────────────────────
# ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# configure root logger
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s"
)

file_handler = RotatingFileHandler(
    filename="logs/flask-app.log",
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=5,
    encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# attach handler to Flask's and werkzeug's loggers
app.logger.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
logging.getLogger("werkzeug").addHandler(file_handler)

app.logger.info("Starting Flask application")

# ─── OAuth / Keycloak setup ───────────────────────────────────────────────────
oauth = OAuth(app)
oauth.register(
    name="keycloak",
    client_id=os.getenv("KEYCLOAK_CLIENT_ID"),
    client_secret=os.getenv("KEYCLOAK_CLIENT_SECRET"),
    server_metadata_url=os.getenv("KEYCLOAK_METADATA_URL"),
    client_kwargs={
        "scope": "openid profile email",
        "prompt": "login",
    },
)

# ─── Role check decorator ──────────────────────────────────────────────────────
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                app.logger.warning(f"Unauthorized access attempt to {url_for(f.__name__)}")
                return redirect(url_for('login'))
            user_roles = session['user'].get('realm_access', {}).get('roles', [])
            if role not in user_roles:
                app.logger.warning(f"Forbidden: user lacks role '{role}' for {url_for(f.__name__)}")
                return "<h1>403 Forbidden</h1><p>You do not have permission to access this page.</p>", 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ─── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    user = session.get("user")
    return render_template('index.html', user=user)

@app.route("/login")
def login():
    session.clear()
    nonce = os.urandom(16).hex()
    session["nonce"] = nonce
    redirect_uri = url_for("auth", _external=True)
    return oauth.keycloak.authorize_redirect(redirect_uri, nonce=nonce)

@app.route("/auth")
def auth():
    try:
        token = oauth.keycloak.authorize_access_token()
        app.logger.info(f"OAuth token received: {token.keys()}")
        nonce = session.pop("nonce", None)
        user = oauth.keycloak.parse_id_token(token, nonce=nonce)
        session["user"] = user
        app.logger.info(f"User logged in: {user.get('preferred_username')}")
        return redirect(url_for("index"))
    except OAuthError as e:
        app.logger.error(f"OAuthError during auth: {e.error} - {e.description}")
        return f"<h1>Authentication failed</h1><p>{e.error}: {e.description}</p>", 400
    except Exception as e:
        app.logger.exception("Unexpected error during auth")
        return f"<h1>Unexpected error</h1><p>{str(e)}</p>", 500

@app.route("/protected")
def protected():
    if 'user' not in session:
        return "<h1>401 Unauthorized</h1><p>You must log in to access this page.</p>", 401
    return render_template('protected.html')

@app.route("/admin")
@role_required("admin")
def admin():
    return render_template('admin.html')

@app.route("/user")
@role_required("user")
def user_page():
    return render_template('user.html')

@app.route("/manager")
@role_required("manager")
def manager_page():
    return render_template('manager.html')

@app.route("/viewer")
@role_required("viewer")
def viewer_page():
    return render_template('viewer.html')

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    redirect_uri = url_for('index', _external=True)
    logout_url = f"{os.getenv('KEYCLOAK_LOGOUT_URL')}?redirect_uri={redirect_uri}"
    app.logger.info("User logged out, redirecting to Keycloak logout")
    return redirect(logout_url)

# ─── Error handlers ────────────────────────────────────────────────────────────
@app.errorhandler(401)
def unauthorized_error(error):
    return render_template_string("<h1>401 Unauthorized</h1><p>You must log in to access this page.</p>"), 401

@app.errorhandler(403)
def forbidden_error(error):
    return render_template_string("<h1>403 Forbidden</h1><p>You do not have permission to access this page.</p>"), 403

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
