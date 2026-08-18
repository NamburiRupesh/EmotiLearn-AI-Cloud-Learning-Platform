from flask import Flask, render_template
from flask_cors import CORS

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

CORS(app)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/student')
def student():
    return render_template('student_dashboard.html')


@app.route('/teacher')
def teacher():
    return render_template('teacher_dashboard.html')


@app.route('/parent')
def parent():
    return render_template('parent_dashboard.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
