from flask import jsonify
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
    jwt_required,
    get_jwt_identity
)
from flask_restful import Resource, reqparse, abort

from application.funcs.password import verify_password
from application.database import db
from application.user.models import User


class LoginEndpoint(Resource):
    login_parser = reqparse.RequestParser()
    login_parser.add_argument('email', type=str, required=True)
    login_parser.add_argument('password', type=str, required=True)

    def post(self):
        args = self.login_parser.parse_args()
        email, password = args['email'], args['password']

        user_db: User = db.session.query(User).filter(User.email == email, User.enabled == True).first()

        if not user_db or not verify_password(user_db.password, password):
            abort(401, message='Email or password is not correct!')

        access_token = create_access_token(identity=email)
        response = jsonify({'access_token': access_token})
        set_access_cookies(response, access_token)

        return response


class LogoutEndpoint(Resource):
    def get(self):
        response = jsonify({"msg": "logout successful"})
        unset_jwt_cookies(response)
        return response


class RefreshTokenEndpoint(Resource):
    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return jsonify(access_token=access_token)
