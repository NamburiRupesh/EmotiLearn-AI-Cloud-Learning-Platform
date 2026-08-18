import os
from flask import Blueprint, request, jsonify, session, redirect, url_for
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth


auth = Blueprint("auth", __name__)
ALLOWED_ROLES = {"student", "teacher", "parent"}

# Google OAuth is configured by app.py through init_oauth().
oauth = OAuth()

def init_oauth(app):
    oauth.init_app(app)
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    if client_id and client_secret:
        oauth.register(
            name="google",
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )


def _close(connection, cursor):
    if cursor:
        cursor.close()
    if connection:
        connection.close()


@auth.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role = data.get("role", "").strip().lower()

    if not name or not email or not password or role not in ALLOWED_ROLES:
        return jsonify({"message": "Please provide valid name, email, password and role."}), 400
    if len(password) < 8:
        return jsonify({"message": "Password must contain at least 8 characters."}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT user_id FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            return jsonify({"message": "An account with this email already exists."}), 409

        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users(name,email,password_hash,role) VALUES(%s,%s,%s,%s)",
            (name, email, password_hash, role),
        )
        connection.commit()
        return jsonify({"message": "Account created successfully. Please sign in."}), 201
    finally:
        _close(connection, cursor)


@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
    finally:
        _close(connection, cursor)

    if not user or not user.get("password_hash") or not check_password_hash(user["password_hash"], password):
        return jsonify({"message": "Invalid email or password."}), 401

    session.clear()
    session["user_id"] = user["user_id"]
    session["name"] = user["name"]
    session["role"] = user["role"]
    return jsonify({"message": "Login successful", "role": user["role"], "redirect": "/dashboard"})


@auth.route("/google")
def google_login():
    google = oauth.create_client("google")
    if google is None:
        return "Google Sign-In is not configured. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to your .env file.", 503

    # Keep role selected on the login page if supplied.
    role = request.args.get("role", "student").lower()
    if role not in ALLOWED_ROLES:
        role = "student"
    session["google_role"] = role
    redirect_uri = url_for("auth.google_callback", _external=True)
    return google.authorize_redirect(redirect_uri)


@auth.route("/google/callback")
def google_callback():
    google = oauth.create_client("google")
    if google is None:
        return "Google Sign-In is not configured. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to your .env file.", 503

    try:
        token = google.authorize_access_token()
        user_info = token.get("userinfo")
        if not user_info:
            user_info = google.userinfo()
    except Exception:
        return "Google authentication failed. Please try again.", 401

    email = (user_info.get("email") or "").strip().lower()
    name = user_info.get("name") or email.split("@")[0]
    google_id = user_info.get("sub")
    picture = user_info.get("picture")
    role = session.pop("google_role", "student")

    if not email or not google_id:
        return "Google did not provide the required account information.", 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user:
            cursor.execute(
                "UPDATE users SET google_id=%s, profile_image=COALESCE(%s, profile_image) WHERE user_id=%s",
                (google_id, picture, user["user_id"]),
            )
            connection.commit()
        else:
            cursor.execute(
                "INSERT INTO users(name,email,password_hash,google_id,profile_image,role) VALUES(%s,%s,NULL,%s,%s,%s)",
                (name, email, google_id, picture, role),
            )
            connection.commit()
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()
    finally:
        _close(connection, cursor)

    session.clear()
    session["user_id"] = user["user_id"]
    session["name"] = user["name"]
    session["role"] = user["role"]
    return redirect(url_for("dashboard"))


@auth.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully", "redirect": "/login"})
