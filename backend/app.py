import os
from flask import Flask, render_template, session, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv

from auth import auth
from database import get_db_connection

load_dotenv()

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret-key")

CORS(app)
app.register_blueprint(auth, url_prefix="/auth")


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

    stats = {
        "courses": 0,
        "students": 0,
        "quizzes": 0,
        "assignments": 0,
    }
    recent_courses = []

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        teacher_id = session["user_id"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM courses WHERE teacher_id=%s",
            (teacher_id,)
        )
        stats["courses"] = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT COUNT(DISTINCT e.student_id) AS total
            FROM enrollments e
            INNER JOIN courses c ON c.course_id = e.course_id
            WHERE c.teacher_id=%s
            """,
            (teacher_id,)
        )
        stats["students"] = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM quizzes q
            INNER JOIN courses c ON c.course_id = q.course_id
            WHERE c.teacher_id=%s
            """,
            (teacher_id,)
        )
        stats["quizzes"] = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM assignments a
            INNER JOIN courses c ON c.course_id = a.course_id
            WHERE c.teacher_id=%s
            """,
            (teacher_id,)
        )
        stats["assignments"] = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT course_id, course_name, description, created_at
            FROM courses
            WHERE teacher_id=%s
            ORDER BY created_at DESC
            LIMIT 5
            """,
            (teacher_id,)
        )
        recent_courses = cursor.fetchall()

    except Exception:
        # Keep the dashboard available even when the database is not ready.
        stats = {key: 0 for key in stats}
        recent_courses = []

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return render_template(
        "teacher_dashboard.html",
        stats=stats,
        recent_courses=recent_courses
    )


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
