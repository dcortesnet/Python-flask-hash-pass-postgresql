from flask import Flask, request, jsonify
import hashlib
import psycopg2

app = Flask(__name__)

connection = psycopg2.connect(
    dbname="test",
    user="postgres",
    password="123456",
    host="localhost",
)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/register', methods=['POST'])
def register():
    cursor = connection.cursor()
    try:
        body = request.get_json()
        email = body.get('email')
        password = body.get('password')

        if not email or not password:
            return jsonify({"message": "Missing email or password"}), 400

        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
        connection.commit()
        
        return jsonify({'message': 'Registration successful'}), 201
    except Exception as e:
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/login', methods=['POST'])
def login():
    cursor = connection.cursor()
    try:
        body = request.get_json()
        email = body.get('email')
        password = body.get('password')

        if not email or not password:
            return jsonify({"message": "Missing email or password"}), 400
        cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        
        if result is None:
            return jsonify({'message': 'User not register'}), 404
        
        hashed_password = result[0]
        if hashlib.sha256(password.encode('utf-8')).hexdigest() == hashed_password:
            return jsonify({'message': 'Login successful'}), 200
        return jsonify({'message': 'Invalid password'}), 401

    except Exception as e:
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500
    finally:
        cursor.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
