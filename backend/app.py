import os
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from auth import auth
from database import get_db_connection

load_dotenv()

app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
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
    if role == "admin":
        return redirect(url_for("admin_dashboard"))
    session.clear()
    return redirect(url_for("login_page"))

@app.route("/student")
def student_dashboard():
    if session.get("role") != "student":
        return redirect(url_for("login_page"))
    enrolled_courses, available_courses = [], []
    connection = cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        student_id = session["user_id"]
        cursor.execute("""
            SELECT c.course_id, c.course_name, c.description, u.name AS teacher_name
            FROM enrollments e
            INNER JOIN courses c ON c.course_id = e.course_id
            INNER JOIN users u ON u.user_id = c.teacher_id
            WHERE e.student_id=%s ORDER BY c.course_name
        """, (student_id,))
        enrolled_courses = cursor.fetchall()
        cursor.execute("""
            SELECT c.course_id, c.course_name, c.description, u.name AS teacher_name
            FROM courses c
            INNER JOIN users u ON u.user_id = c.teacher_id
            WHERE NOT EXISTS (SELECT 1 FROM enrollments e WHERE e.student_id=%s AND e.course_id=c.course_id)
            ORDER BY c.created_at DESC
        """, (student_id,))
        available_courses = cursor.fetchall()
    except Exception:
        enrolled_courses, available_courses = [], []
    finally:
        if cursor: cursor.close()
        if connection: connection.close()
    return render_template("student_dashboard.html", enrolled_courses=enrolled_courses, available_courses=available_courses)

@app.route("/student/courses/<int:course_id>/join", methods=["POST"])
def join_course(course_id):
    if session.get("role") != "student":
        return jsonify({"message": "Student authentication required."}), 403
    connection = cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        student_id = session["user_id"]
        cursor.execute("SELECT course_id FROM courses WHERE course_id=%s", (course_id,))
        if not cursor.fetchone(): return jsonify({"message": "Course not found."}), 404
        cursor.execute("SELECT enrollment_id FROM enrollments WHERE student_id=%s AND course_id=%s", (student_id, course_id))
        if cursor.fetchone(): return jsonify({"message": "You are already enrolled in this course."}), 409
        cursor.execute("INSERT INTO enrollments (student_id, course_id) VALUES (%s, %s)", (student_id, course_id))
        connection.commit()
        return jsonify({"message": "Course joined successfully."}), 201
    except Exception:
        if connection: connection.rollback()
        return jsonify({"message": "Unable to join the course right now."}), 500
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

@app.route("/teacher")
def teacher_dashboard():
    if session.get("role") != "teacher":
        return redirect(url_for("login_page"))
    stats = {"courses": 0, "students": 0, "quizzes": 0, "assignments": 0}
    recent_courses, students = [], []
    connection = cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        teacher_id = session["user_id"]
        queries = [
            ("courses", "SELECT COUNT(*) AS total FROM courses WHERE teacher_id=%s"),
            ("students", "SELECT COUNT(DISTINCT e.student_id) AS total FROM enrollments e INNER JOIN courses c ON c.course_id=e.course_id WHERE c.teacher_id=%s"),
            ("quizzes", "SELECT COUNT(*) AS total FROM quizzes q INNER JOIN courses c ON c.course_id=q.course_id WHERE c.teacher_id=%s"),
            ("assignments", "SELECT COUNT(*) AS total FROM assignments a INNER JOIN courses c ON c.course_id=a.course_id WHERE c.teacher_id=%s")]
        for key, sql in queries:
            cursor.execute(sql, (teacher_id,)); stats[key] = cursor.fetchone()["total"]
        cursor.execute("SELECT course_id, course_name, description, created_at FROM courses WHERE teacher_id=%s ORDER BY created_at DESC LIMIT 5", (teacher_id,))
        recent_courses = cursor.fetchall()
        cursor.execute("""
            SELECT DISTINCT u.user_id, u.name, u.email, c.course_name
            FROM users u INNER JOIN enrollments e ON e.student_id=u.user_id
            INNER JOIN courses c ON c.course_id=e.course_id
            WHERE c.teacher_id=%s AND u.role='student' ORDER BY u.name, c.course_name
        """, (teacher_id,))
        students = cursor.fetchall()
    except Exception:
        stats = {key: 0 for key in stats}; recent_courses, students = [], []
    finally:
        if cursor: cursor.close()
        if connection: connection.close()
    return render_template("teacher_dashboard.html", stats=stats, recent_courses=recent_courses, students=students)

@app.route("/teacher/courses", methods=["POST"])
def create_course():
    if session.get("role") != "teacher": return jsonify({"message": "Teacher authentication required."}), 403
    data = request.get_json(silent=True) or {}
    course_name, description = (data.get("course_name") or "").strip(), (data.get("description") or "").strip()
    if not course_name: return jsonify({"message": "Course name is required."}), 400
    if len(course_name) > 100: return jsonify({"message": "Course name must be 100 characters or less."}), 400
    connection = cursor = None
    try:
        connection = get_db_connection(); cursor = connection.cursor()
        cursor.execute("INSERT INTO courses (course_name,description,teacher_id) VALUES (%s,%s,%s)", (course_name, description, session["user_id"]))
        connection.commit(); return jsonify({"message": "Course created successfully."}), 201
    except Exception:
        if connection: connection.rollback()
        return jsonify({"message": "Unable to create course. Check your database connection."}), 500
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

@app.route("/teacher/courses/<int:course_id>/lectures", methods=["GET", "POST"])
def teacher_lectures(course_id):
    if session.get("role") != "teacher":
        if request.method == "POST":
            return jsonify({"message": "Teacher authentication required."}), 403
        return redirect(url_for("login_page"))

    connection = cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT course_id, course_name, description FROM courses WHERE course_id=%s AND teacher_id=%s",
            (course_id, session["user_id"]),
        )
        course = cursor.fetchone()
        if not course:
            if request.method == "POST":
                return jsonify({"message": "Course not found or access denied."}), 404
            return redirect(url_for("teacher_dashboard"))

        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            title = (data.get("title") or "").strip()
            video_url = (data.get("video_url") or "").strip()
            notes_url = (data.get("notes_url") or "").strip()
            if not title:
                return jsonify({"message": "Lecture title is required."}), 400
            cursor.execute(
                "INSERT INTO lectures (course_id,title,video_url,notes_url) VALUES (%s,%s,%s,%s)",
                (course_id, title, video_url, notes_url),
            )
            connection.commit()
            return jsonify({"message": "Lecture added successfully."}), 201

        cursor.execute(
            "SELECT lecture_id, title, video_url, notes_url FROM lectures WHERE course_id=%s ORDER BY lecture_id DESC",
            (course_id,),
        )
        lectures = cursor.fetchall()
        return render_template("teacher_lectures.html", course=course, lectures=lectures)
    except Exception:
        if connection and request.method == "POST":
            connection.rollback()
        if request.method == "POST":
            return jsonify({"message": "Unable to save lecture. Check your database connection."}), 500
        return redirect(url_for("teacher_dashboard"))
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("login_page"))
    return render_template("admin_dashboard.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
