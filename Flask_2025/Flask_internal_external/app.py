from flask import Flask, request, jsonify, make_response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from authlib.integrations.flask_client import OAuth  # Import Authlib for OAuth

app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Google OAuth Configuration
app.config['GOOGLE_CLIENT_ID'] = 'your-google-client-id'  # Replace with your Client ID
app.config['GOOGLE_CLIENT_SECRET'] = 'your-google-client-secret'  # Replace with your Client Secret

db = SQLAlchemy(app)

# Initialize OAuth
oauth = OAuth(app)

# Register Google OAuth provider
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'email profile'},  # Request email and profile info
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs'  # For token verification
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=True)  # Allow nullable for OAuth users
    role = db.Column(db.String(20), default='user')

# ---------------------- Helper Decorators ----------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(email=data['email']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(email=data['email']).first()
            if current_user.role != 'admin':
                return jsonify({'message': 'Admin access required!'}), 403
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# ---------------------- Existing Routes ----------------------
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or not all(k in data for k in ('firstname', 'lastname', 'email', 'password')):
        return jsonify({'message': 'Firstname, lastname, email and password are required!'}), 400

    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'message': 'Email already exists!'}), 400

    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        firstname=data['firstname'],
        lastname=data['lastname'],
        email=data['email'],
        password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully!'}), 201

@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    if not auth or not auth.get('email') or not auth.get('password'):
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(email=auth['email']).first()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth['password']):
        token = jwt.encode(
            {'email': user.email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return jsonify({'token': token})
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

@app.route('/adminlogin', methods=['POST'])
def adminlogin():
    auth = request.get_json()
    if not auth or not auth.get('email') or not auth.get('password'):
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(email=auth['email']).first()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if user.role != 'admin':
        return make_response('Unauthorized', 403, {'WWW-Authenticate': 'Basic realm="Admin access required!"'})

    if check_password_hash(user.password, auth['password']):
        token = jwt.encode(
            {'email': user.email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return jsonify({'token': token})
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

@app.route('/user', methods=['GET'])
@token_required
def user_route(current_user):
    return jsonify({'message': f'Hello {current_user.firstname} {current_user.lastname}! This is a user-accessible route.'})

@app.route('/admin', methods=['GET'])
@admin_required
def admin_route(current_user):
    return jsonify({'message': f'Hello Admin {current_user.firstname} {current_user.lastname}!'})

@app.route('/profile', methods=['GET'])
@token_required
def view_profile(current_user):
    return jsonify({
        'firstname': current_user.firstname,
        'lastname': current_user.lastname,
        'email': current_user.email,
        'role': current_user.role
    })

# ---------------------- Google OAuth Routes ----------------------
@app.route('/login/google')
def google_login():
    # Redirect to Google's OAuth authorization page
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/google/callback')
def google_callback():
    # Handle the callback from Google
    token = google.authorize_access_token()  # Get the access token
    user_info = google.get('userinfo').json()  # Fetch user info (email, name, etc.)

    email = user_info['email']
    firstname = user_info.get('given_name', 'Unknown')
    lastname = user_info.get('family_name', 'Unknown')

    # Check if the user already exists in the database
    user = User.query.filter_by(email=email).first()
    if not user:
        # Create a new user (no password since they’re using Google OAuth)
        user = User(
            firstname=firstname,
            lastname=lastname,
            email=email,
            password=None,  # No password for OAuth users
            role='user'
        )
        db.session.add(user)
        db.session.commit()

    # Generate a JWT token for the user
    jwt_token = jwt.encode(
        {'email': user.email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )

    return jsonify({'token': jwt_token})

# ---------------------- Main ----------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8080)