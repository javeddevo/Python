from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from functools import wraps
import uuid

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change to secure key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

# Simulated book database
db = [
    {'id': 1, 'name': 'John Doe', 'author': 'John', 'description': 'This is a test book'},
    {'id': 2, 'name': 'Jane Doe', 'author': 'Jane', 'description': 'This is another test book'},
    {'id': 3, 'name': 'Jim Doe', 'author': 'Jim', 'description': 'This is yet another test book'}
]

# Simulated user database
users_db = []

# Role-based decorator
def role_required(roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') not in roles:
                return jsonify({'error': 'Unauthorized access'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    role = data.get('role', 'user')  # default role is user

    if not email or not password or not confirm_password:
        return jsonify({'error': 'Missing required fields'}), 400

    if any(user['email'] == email for user in users_db):
        return jsonify({'error': 'Email already in use'}), 400

    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    hashed_password = generate_password_hash(password)

    new_user = {
        'id': len(users_db) + 1,
        'email': email,
        'password': hashed_password,
        'role': role,
    }

    users_db.append(new_user)

    return jsonify({'message': 'User registered successfully!'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = next((u for u in users_db if u['email'] == email), None)
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = create_access_token(identity=user['email'], additional_claims={'role': user['role']})
    return jsonify({'access_token': token, 'role': user['role']}), 200

@app.route('/', methods=['GET'])
def hello_world():
    return jsonify('<h1>Hello, World!</h1>')

@app.route('/books', methods=['GET'])
@jwt_required()
def get_books():
    return jsonify(db)

@app.route('/books/<int:id>', methods=['GET'])
@jwt_required()
def get_book(id):
    book = next((book for book in db if book['id'] == id), None)
    if book:
        return jsonify(book)
    return {'error': 'Book not found'}, 404

@app.route('/books/search', methods=['GET'])
@jwt_required()
def search_books():
    author = request.args.get('author')
    books = [b for b in db if b['author'] == author]
    if books:
        return jsonify(books)
    return {'error': 'Book not found'}, 404

@app.route('/books', methods=['POST'])
@role_required(['admin'])
def add_book():
    book_details = {
        'id': len(db) + 1,
        'name': request.json['name'],
        'author': request.json['author'],
        'description': request.json['description']
    }
    db.append(book_details)
    return jsonify(book_details), 201

@app.route('/books/<int:id>', methods=['PUT'])
@role_required(['admin'])
def update_book(id):
    book = next((book for book in db if book['id'] == id), None)
    if book:
        book['name'] = request.json['name']
        book['author'] = request.json['author']
        book['description'] = request.json['description']
        return jsonify(book)
    return {'error': 'Book not found'}, 404

@app.route('/books/<int:id>', methods=['DELETE'])
@role_required(['admin'])
def delete_book(id):
    for index, book in enumerate(db):
        if book['id'] == id:
            db.pop(index)
            return jsonify({'message': f'Book with id:{id} is deleted successfully'}), 200
    return jsonify({'error': 'Book not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)


#grok
# from flask import Flask, request, jsonify
# from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt
# from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import timedelta
# from functools import wraps
# import os
# import logging
# from dotenv import load_dotenv

# load_dotenv()

# app = Flask(__name__)
# app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
# jwt = JWTManager(app)

# # Configure logging
# logging.basicConfig(filename='app.log', level=logging.INFO)

# # Simulated databases
# db = [
#     {'id': 1, 'name': 'John Doe', 'author': 'John', 'description': 'This is a test book'},
#     {'id': 2, 'name': 'Jane Doe', 'author': 'Jane', 'description': 'This is another test book'},
#     {'id': 3, 'name': 'Jim Doe', 'author': 'Jim', 'description': 'This is yet another test book'}
# ]
# users_db = []
# ADMIN_SECRET = os.getenv('ADMIN_SECRET', 'super-secret-admin-key')

# # Role-based decorator
# def role_required(roles):
#     def decorator(fn):
#         @wraps(fn)
#         @jwt_required()
#         def wrapper(*args, **kwargs):
#             claims = get_jwt()
#             if claims.get('role') not in roles:
#                 return jsonify({'error': 'Unauthorized access'}), 403
#             return fn(*args, **kwargs)
#         return wrapper
#     return decorator

# @app.route('/signup', methods=['POST'])
# def signup():
#     data = request.get_json()
#     email = data.get('email')
#     password = data.get('password')
#     confirm_password = data.get('confirm_password')

#     if not email or not password or not confirm_password:
#         return jsonify({'error': 'Missing required fields'}), 400

#     if any(user['email'] == email for user in users_db):
#         return jsonify({'error': 'Email already in use'}), 400

#     if password != confirm_password:
#         return jsonify({'error': 'Passwords do not match'}), 400

#     hashed_password = generate_password_hash(password)

#     new_user = {
#         'id': len(users_db) + 1,
#         'email': email,
#         'password': hashed_password,
#         'role': 'user',
#     }

#     users_db.append(new_user)
#     return jsonify({'message': 'User registered successfully!'}), 201

# @app.route('/admin/signup', methods=['POST'])
# def admin_signup():
#     data = request.get_json()
#     email = data.get('email')
#     password = data.get('password')
#     confirm_password = data.get('confirm_password')
#     admin_secret = data.get('admin_secret')

#     if admin_secret != ADMIN_SECRET:
#         return jsonify({'error': 'Invalid admin secret key'}), 403

#     if not email or not password or not confirm_password:
#         return jsonify({'error': 'Missing required fields'}), 400

#     if any(user['email'] == email for user in users_db):
#         return jsonify({'error': 'Email already in use'}), 400

#     if password != confirm_password:
#         return jsonify({'error': 'Passwords do not match'}), 400

#     hashed_password = generate_password_hash(password)

#     new_admin = {
#         'id': len(users_db) + 1,
#         'email': email,
#         'password': hashed_password,
#         'role': 'admin',
#     }

#     users_db.append(new_admin)
#     logging.info(f"Admin created: {email}")
#     return jsonify({'message': 'Admin registered successfully!'}), 201

# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     email = data.get('email')
#     password = data.get('password')

#     user = next((u for u in users_db if u['email'] == email), None)
#     if not user or not check_password_hash(user['password'], password):
#         logging.warning(f"Failed login attempt for email: {email}")
#         return jsonify({'error': 'Invalid credentials'}), 401

#     token = create_access_token(identity=user['email'], additional_claims={'role': user['role']})
#     if user['role'] == 'admin':
#         logging.info(f"Admin login successful for email: {email}")
#     else:
#         logging.info(f"User login successful for email: {email}")
#     return jsonify({'access_token': token, 'role': user['role']}), 200

# @app.route('/users', methods=['GET'])
# @role_required(['admin'])
# def get_users():
#     return jsonify([{'id': u['id'], 'email': u['email'], 'role': u['role']} for u in users_db]), 200

# @app.route('/users/<int:id>', methods=['PUT'])
# @role_required(['admin'])
# def update_user(id):
#     user = next((u for u in users_db if u['id'] == id), None)
#     if not user:
#         return jsonify({'error': 'User not found'}), 404

#     data = request.get_json()
#     if 'role' in data:
#         user['role'] = data['role']
#     if 'email' in data:
#         user['email'] = data['email']
#     if 'password' in data:
#         user['password'] = generate_password_hash(data['password'])

#     logging.info(f"Admin updated user ID: {id}")
#     return jsonify({'message': 'User updated successfully'}), 200

# @app.route('/users/<int:id>', methods=['DELETE'])
# @role_required(['admin'])
# def delete_user(id):
#     for index, user in enumerate(users_db):
#         if user['id'] == id:
#             users_db.pop(index)
#             logging.info(f"Admin deleted user ID: {id}")
#             return jsonify({'message': f'User with id:{id} deleted successfully'}), 200
#     return jsonify({'error': 'User not found'}), 404

# # Existing book-related endpoints remain unchanged
# @app.route('/', methods=['GET'])
# def hello_world():
#     return jsonify('<h1>Hello, World!</h1>')

# @app.route('/books', methods=['GET'])
# @jwt_required()
# def get_books():
#     return jsonify(db)

# @app.route('/books/<int:id>', methods=['GET'])
# @jwt_required()
# def get_book(id):
#     book = next((book for book in db if book['id'] == id), None)
#     if book:
#         return jsonify(book)
#     return {'error': 'Book not found'}, 404

# @app.route('/books/search', methods=['GET'])
# @jwt_required()
# def search_books():
#     author = request.args.get('author')
#     books = [b for b in db if b['author'] == author]
#     if books:
#         return jsonify(books)
#     return {'error': 'Book not found'}, 404

# @app.route('/books', methods=['POST'])
# @role_required(['admin'])
# def add_book():
#     book_details = {
#         'id': len(db) + 1,
#         'name': request.json['name'],
#         'author': request.json['author'],
#         'description': request.json['description']
#     }
#     db.append(book_details)
#     logging.info(f"Admin added book: {book_details['name']}")
#     return jsonify(book_details), 201

# @app.route('/books/<int:id>', methods=['PUT'])
# @role_required(['admin'])
# def update_book(id):
#     book = next((book for book in db if book['id'] == id), None)
#     if book:
#         book['name'] = request.json['name']
#         book['author'] = request.json['author']
#         book['description'] = request.json['description']
#         logging.info(f"Admin updated book ID: {id}")
#         return jsonify(book)
#     return {'error': 'Book not found'}, 404

# @app.route('/books/<int:id>', methods=['DELETE'])
# @role_required(['admin'])
# def delete_book(id):
#     for index, book in enumerate(db):
#         if book['id'] == id:
#             db.pop(index)
#             logging.info(f"Admin deleted book ID: {id}")
#             return jsonify({'message': f'Book with id:{id} is deleted successfully'}), 200
#     return jsonify({'error': 'Book not found'}), 404

# if __name__ == '__main__':
#     app.run(debug=True)