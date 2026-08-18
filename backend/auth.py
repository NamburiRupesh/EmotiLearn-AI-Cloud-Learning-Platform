from flask import Blueprint, request, jsonify, session
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint("auth", __name__)
ALLOWED_ROLES = {"student", "teacher", "parent"}


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

    return jsonify({
        "message": "Login successful",
        "role": user["role"],
        "redirect": "/dashboard"
    })


@auth.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully", "redirect": "/login"})
