from flask import Blueprint, request
from flask_jwt_extended.utils import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import null
from werkzeug.routing import ValidationError
from .model import UserSchema, UserModel

# random passowrd for google user
import string
import random

# Google one tap auth
from google.oauth2 import id_token
from google.auth.transport import requests


from flask_restful import Api, Resource

auth = Blueprint('auth', __name__, url_prefix='/auth')
api = Api(auth)

users_schema = UserSchema()

class Register(Resource):
    def post(self):
        try:
            print(request.json)
            user_data = users_schema.load(request.json, partial=True)
            print(user_data)
            new_user = UserModel(user_data)
            new_user.save_db()
            
            return {'msg': 'successfully registered.'}, 200

        except ValidationError as error:
            print(error)
            return {'msg': 'Validation error'}, 400

        except Exception as e:
            print(e)
            return {'msg': 'errors'}, 500

class Login(Resource):
    def post(self):
        try:
            user_input = request.json
            user_data = users_schema.load(user_input, partial=True)

            username = user_data['username']
            password = user_data['password']

            query = UserModel.get_user(username)
            if query != None and query.verify_password(password):
                access_token = create_access_token(identity=query.uid)
                refresh_token = create_refresh_token(identity=query.uid)
                return {
                    'msg':'Login successfully.',
                    'username': query.username,
                    'access': access_token,
                    'refresh': refresh_token
                    }, 200
            else:
                return {'msg':'Incorrect username or password.',
                        'username': '',
                        'access': '',
                        'refresh': ''}, 400

        except ValidationError as error:
            return {'msg':'Incorrect username or password.',
                    'username': '',
                    'access': '',
                    'refresh': ''}, 400

        except Exception as e:
            print(e)
            return {'msg':'Server error.',
                    'username': '',
                    'access': '',
                    'refresh': ''}, 400

class Refresh(Resource):

    @jwt_required(refresh=True)
    def post(self):
        try:
            identity = get_jwt_identity()
            payload = get_jwt()
            access_token = create_access_token(identity=identity)
            return {'msg':'Refresh token successful.',
                    'access': access_token,}, 200
        except Exception as e:
            print(e)
            return {'msg': 'Server error.',
                    'access': ''}, 500

# Google Login handler
class GoogleOneTap(Resource):
    def post(self):
        try:

            client_id = '568589005709-nd5dsacqqh8n2jlfe8j4be3jedo4senq.apps.googleusercontent.com'

            idToken = request.json['idToken']
            # print(idToken)

            idinfo = id_token.verify_oauth2_token(idToken, requests.Request(), client_id)
            userid = idinfo['sub']
            print(userid)
            
            query = UserModel.get_user(str(userid))
            if query == None:
                # user sign up flow
                print(1)
                user_model = { 'username':str(userid), 'password': UserModel.generate_random_password()}
                new_user = UserModel(user_model)
                new_user.save_db()
                # login newly created user
                query_new_user = UserModel.get_user(str(userid))
                access_token = create_access_token(identity=query_new_user.uid)
                refresh_token = create_refresh_token(identity=query_new_user.uid)
                return {
                    'msg':'Sign up and login successfully.',
                    'username': query_new_user.username,
                    'access': access_token,
                    'refresh': refresh_token
                    }, 200
            else:
                # user login flow
                print(2)
                access_token = create_access_token(identity=query.uid)
                refresh_token = create_refresh_token(identity=query.uid)
                return {
                    'msg':'Login successfully.',
                    'username': query.username,
                    'access': access_token,
                    'refresh': refresh_token
                    }, 200
            
        except ValueError:
            return {
                'msg':'Invalid token.',
                'username': '',
                'access': '',
                'refresh': ''
            }, 400

        except Exception as e:
            print(e)
            return {
                'msg':'Login failed.',
                'username': '',
                'access': '',
                'refresh': ''
            }, 400

api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Refresh, '/refresh')
api.add_resource(GoogleOneTap,'/googleOneTap')
