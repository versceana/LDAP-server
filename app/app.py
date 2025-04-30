import os
from flask import Flask, redirect, url_for, session, render_template_string
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
            # Проверка авторизации пользователя
            if 'user' not in session:
                return redirect(url_for('login'))

            # Проверка роли
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
        return render_template_string('''
            <h1>Welcome, {{ user['preferred_username'] }}!</h1>
            <form action="{{ url_for('logout') }}" method="post">
                <button type="submit">Logout</button>
            </form>
            <a href="{{ url_for('protected') }}">Go to Protected Page</a><br>
            <a href="{{ url_for('admin') }}">Go to Admin Page</a><br>
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
    nonce = os.urandom(16).hex()  # Генерация nonce для защиты от CSRF
    redirect_uri = url_for("auth", _external=True)
    return oauth.keycloak.authorize_redirect(redirect_uri, nonce=nonce)


# Обработка авторизации
@app.route("/auth")
def auth():
    try:
        token = oauth.keycloak.authorize_access_token()
        nonce = session.pop("nonce", None)
        user = oauth.keycloak.parse_id_token(token, nonce=nonce)
        session["user"] = user
        return redirect("/")
    except OAuthError as e:
        return f"<h1>Authentication failed</h1><p>{e.error}: {e.description}</p>", 400
    except Exception as e:
        return f"<h1>Unexpected error</h1><p>{str(e)}</p>", 500


# Страница с ограниченным доступом
@app.route("/protected")
def protected():
    if 'user' not in session:
        return "<h1>401 Unauthorized</h1><p>You must log in to access this page.</p>", 401
    return "<h1>Welcome to the protected page!</h1>"


# Страница для администраторов (доступна только пользователям с ролью 'admin')
@app.route("/admin")
@role_required("admin")
def admin():
    return "<h1>Welcome to the Admin Page!</h1>"


# Страница выхода
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    redirect_uri = url_for('index', _external=True)  # Главная страница приложения
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
    app.run(host="0.0.0.0", port=5001, debug=True)
