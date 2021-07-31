from flask import jsonify
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
    jwt_required,
    get_jwt_identity,
    create_refresh_token)
from flask_restful import Resource, reqparse, abort

from application.email.sender import send_email
from application.funcs.confirmation_code import generate_code
from application.funcs.password import verify_password
from application.database import db
from application.user.models import User, ForgotPassword


class ForgotPasswordEndpoint(Resource):
    forgot_password = reqparse.RequestParser()
    forgot_password.add_argument('email', type=str, required=True)

    def put(self):
        # Request change password code
        args: dict = self.forgot_password.parse_args()
        email = args['email']

        user_from_db: User = db.session.query(User)\
            .filter(User.email == email, User.enabled == True)\
            .first()
        reset_code = generate_code(6)

        if not user_from_db:
            return

        forgot_password = ForgotPassword(
            user_id=user_from_db.id,
            reset_code=reset_code
        )
        try:
            db.session.add(forgot_password)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return

        send_email(
            to_email=user_from_db.email,
            template_name='reset_code',
            context=dict(reset_code=reset_code)
        )

    def post(self):
        # Perform code
        pass


class LoginEndpoint(Resource):
    login_parser = reqparse.RequestParser()
    login_parser.add_argument('email', type=str, required=True)
    login_parser.add_argument('password', type=str, required=True)

    def post(self):
        args: dict = self.login_parser.parse_args()
        email, password = args['email'], args['password']

        user_db: User = db.session.query(User).filter(User.email == email, User.enabled == True).first()

        if not user_db or not verify_password(user_db.password, password):
            abort(401, message='Email or password is not correct!')

        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)
        response = jsonify({'access_token': access_token, 'refresh_token': refresh_token})
        set_access_cookies(response, access_token)

        return response

    @jwt_required()
    def get(self):
        """Check auth logic, just check and return"""
        # /api/login/ will return True for authenticated user and 401
        return True



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

        response = jsonify(access_token=access_token)

        # Also save new access token into cookie for future work with cookie-based session
        set_access_cookies(response, access_token)
        return response
