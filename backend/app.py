import os
from flask import Flask, render_template, session, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv

from auth import auth, init_oauth

load_dotenv()

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret-key")

CORS(app)
app.register_blueprint(auth, url_prefix="/auth")
init_oauth(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login_page():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/signup")
def signup_page():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("signup.html")


@app.route("/dashboard")
def dashboard():
    role = session.get("role")
    if not role:
        return redirect(url_for("login_page"))

    if role == "student":
        return redirect(url_for("student_dashboard"))
    if role == "teacher":
        return redirect(url_for("teacher_dashboard"))
    if role == "parent":
        return redirect(url_for("parent_dashboard"))
    return redirect(url_for("admin_dashboard"))


@app.route("/student")
def student_dashboard():
    if session.get("role") != "student":
        return redirect(url_for("login_page"))
    return render_template("student_dashboard.html")


@app.route("/teacher")
def teacher_dashboard():
    if session.get("role") != "teacher":
        return redirect(url_for("login_page"))
    return render_template("teacher_dashboard.html")


@app.route("/parent")
def parent_dashboard():
    if session.get("role") != "parent":
        return redirect(url_for("login_page"))
    return render_template("parent_dashboard.html")


@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("login_page"))
    return render_template("admin_dashboard.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
