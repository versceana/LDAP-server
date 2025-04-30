import os
from flask import Flask, redirect, url_for, session, render_template_string, render_template
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client.errors import OAuthError
from dotenv import load_dotenv
from functools import wraps

# Загружаем переменные из .env файла
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
        "prompt": "login"  # всегда заставлять логиниться
    },
)

# Декоратор для проверки ролей
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login'))

            user_roles = session['user'].get('realm_access', {}).get('roles', [])
            if role not in user_roles:
                return "<h1>403 Forbidden</h1><p>You do not have permission to access this page.</p>", 403

            return f(*args, **kwargs)

        return decorated_function
    return decorator

# Главная страница
@app.route("/")
def index():
    user = session.get("user")
    if user:
        return render_template('index.html', user=user)
    else:
        return render_template('index.html')

# Страница входа
@app.route("/login", methods=["GET"])
def login():
    session.clear()
    nonce = os.urandom(16).hex()  # Генерация nonce
    session["nonce"] = nonce
    redirect_uri = url_for("auth", _external=True)
    return oauth.keycloak.authorize_redirect(redirect_uri, nonce=nonce)

# Обработка авторизации
@app.route("/auth")
def auth():
    try:
        token = oauth.keycloak.authorize_access_token()
        print("=== FULL TOKEN DATA ===")
        print(token)

        nonce = session.pop("nonce", None)
        user = oauth.keycloak.parse_id_token(token, nonce=nonce)
        session["user"] = user
        return redirect("/")
    except OAuthError as e:
        return f"<h1>Authentication failed</h1><p>{e.error}: {e.description}</p>", 400
    except Exception as e:
        return f"<h1>Unexpected error</h1><p>{str(e)}</p>", 500

# Общая защищённая страница (только вход)
@app.route("/protected")
def protected():
    if 'user' not in session:
        return "<h1>401 Unauthorized</h1><p>You must log in to access this page.</p>", 401
    return "<h1>Welcome to the protected page!</h1>"

# Страница для администраторов
@app.route("/admin")
@role_required("admin")
def admin():
    return "<h1>Welcome to the Admin Page!</h1>"

# Страница для пользователей с ролью user
@app.route("/user")
@role_required("user")
def user_page():
    return "<h1>Welcome to the User Page!</h1>"

# Страница для пользователей с ролью manager
@app.route("/manager")
@role_required("manager")
def manager_page():
    return "<h1>Welcome to the Manager Page!</h1>"

# Страница для пользователей с ролью viewer
@app.route("/viewer")
@role_required("viewer")
def viewer_page():
    return "<h1>Welcome to the Viewer Page!</h1>"

# Выход
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    redirect_uri = url_for('index', _external=True)
    logout_url = f"{os.getenv('KEYCLOAK_LOGOUT_URL')}?redirect_uri={redirect_uri}"
    print("logout")
    return redirect(logout_url)

# Обработчики ошибок
@app.errorhandler(401)
def unauthorized_error(error):
    return render_template_string("<h1>401 Unauthorized</h1><p>You must log in to access this page.</p>"), 401

@app.errorhandler(403)
def forbidden_error(error):
    return render_template_string("<h1>403 Forbidden</h1><p>You do not have permission to access this page.</p>"), 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)