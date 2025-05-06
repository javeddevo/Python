from functools import wraps
import traceback
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity,create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash
import config
import logging
from logger import setup_logger
from datetime import timedelta 
logger=setup_logger()

app=Flask(__name__)
api=Api(app)
jwt=JWTManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = config.SECRET_KEY  
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)  # Set token expiration to 1 day
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

db=SQLAlchemy(app)

class UserManagement(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(80), unique=True, nullable=False)
    password=db.Column(db.String(500),nullable=False)
    role=db.Column(db.String(80), nullable=False)

    def set_password(self, password):
        self.password=generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)  # hashed password(self.password) is compared with the provided password

with app.app_context():
    db.create_all()

class HomeResource(Resource):
    def get(self):
        return {"message": "Welcome to the Flask Authentication and Authorization API!"}
    
class MemberRegistrationResource(Resource):
    def post(self):
        try:
            data=request.get_json()
            username=data.get('username')
            password=data.get('password')
            role=data.get('role','member')
            hashed_password=generate_password_hash(password)  # Hash the password before storing it

            if not username or not password or not role:
                logger.warning("Missing registration fields.")
                return {"message": "Username, password, and role are required!"}, 400

            if UserManagement.query.filter_by(username=username).first():  #just like select * from member where username=username
                logger.info(f"Registration failed - user '{username}' already exists.")
                return {"message": "User already exists!"}, 409

            new_member=UserManagement(username=username,password=hashed_password,role=role)
            db.session.add(new_member)  # Add the new member to the session
            db.session.commit()
            logger.info(f"User '{username}' registered successfully.")
            return {"message": "User registered successfully!"}, 201
        except Exception as e:
            db.session.rollback()
            logger.error("Exception during registration", exc_info=True)
            return {"message": "An error occurred during registration!"}, 500

class MemberLoginResource(Resource):
    def post(self):
        data=request.get_json()
        username=data.get('username')
        password=data.get('password')

        if not username or not password:
            logger.warning("Missing login fields.")
            return {"message": "Username and password are required!"}, 400

        member=UserManagement.query.filter_by(username=username).first()  #just like select * from member where username=username
        isvalid_password=check_password_hash(member.password, password) if member else False  # Check if the password is vali
        if member and isvalid_password:
            #access_token=create_access_token(identity={"username": member.username})
        #     access_token = create_access_token(identity=str(member.id))
        #     logger.info(f"User '{username}' logged in successfully.")
        #     return {"access_token":access_token}, 200
        # else:
        #     logger.warning(f"Login failed for user '{username}'.")
        #     return {"message": "Invalid credentials!"}, 401
            access_token = create_access_token(identity=str(member.id))
            refresh_token = create_refresh_token(identity=str(member.id))
            logger.info(f"User '{username}' logged in successfully.")
            return {
                "access_token": access_token,
                "refresh_token": refresh_token
            }, 200
        else:
            logger.warning(f"Login failed for user '{username}'.")
            return {"message": "Invalid credentials!"}, 401
        
class TokenRefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user)
        return {"access_token": new_access_token}, 200

# role_required decorator to check user roles
def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            user = UserManagement.query.get(current_user)
            if not user or user.role != role:
                logger.warning(f"Access denied for user '{current_user}'. Required role: {role}.")
                return {"message": "Access denied!"}, 403
            return fn(*args, **kwargs)
        return decorated_function
    return wrapper

class MemberOnlyResource(Resource):
    @jwt_required()
    def get(self):
        current_user=get_jwt_identity()
        member=UserManagement.query.get(current_user)
        return {"message": f"Hello member {member.username}"}, 200
    
class AdminOnlyResource(Resource):
    @jwt_required()
    @role_required('admin')  # Only allow access to admin users
    def get(self):
        current_user=get_jwt_identity()
        member=UserManagement.query.get(current_user)
        return {"message": f"Hello admin {member.username}"}, 200
    
class Welcome(Resource):
    @jwt_required()
    def get(self):
        return "Welcome to the main dashboard!"
    
#add routes to the api
api.add_resource(HomeResource, '/api/v1/')
api.add_resource(MemberRegistrationResource, '/api/v1/register')
api.add_resource(MemberLoginResource, '/api/v1/login')
api.add_resource(TokenRefreshResource, '/api/v1/refresh')
api.add_resource(MemberOnlyResource, '/api/v1/member-only')
api.add_resource(AdminOnlyResource, '/api/v1/admin-only')
api.add_resource(Welcome, '/api/v1/welcome')


if __name__ == '__main__':
    logger.info("App started successfully")
    app.run(debug=True, port=5000)

