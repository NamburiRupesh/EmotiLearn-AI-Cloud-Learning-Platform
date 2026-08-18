from flask import Blueprint, request, jsonify
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint('auth', __name__)


@auth.route('/signup', methods=['POST'])
def signup():
    data = request.json

    name = data['name']
    email = data['email']
    password = generate_password_hash(data['password'])
    role = data['role']

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO users(name,email,password_hash,role) VALUES(%s,%s,%s,%s)",
        (name,email,password,role)
    )

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message':'Account created successfully'})


@auth.route('/login', methods=['POST'])
def login():
    data=request.json

    email=data['email']
    password=data['password']

    connection=get_db_connection()
    cursor=connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE email=%s",
        (email,)
    )

    user=cursor.fetchone()

    cursor.close()
    connection.close()

    if user and check_password_hash(user['password_hash'],password):
        return jsonify({
            'message':'Login successful',
            'role':user['role']
        })

    return jsonify({'message':'Invalid credentials'}),401
