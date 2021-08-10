from datetime import datetime, timedelta
from typing import List

from flask import jsonify
from flask_apispec import marshal_with, MethodResource, use_kwargs, doc
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
    jwt_required,
    get_jwt_identity,
    create_refresh_token
)
from flask_restful import Resource, reqparse, abort

from application.api.auth.docs import (
    LoginPostEndpointResponse,
    LoginPostEndpointRequest,
    LogoutGetResponse,
    ForgotPasswordPutResponse,
    ForgotPasswordPutRequest,
    ForgotPasswordPostRequest,
    ForgotPasswordPostResponse,
    RefreshTokenPostEndpointResponse
)
from application.api.email.sender import send_email
from application.api.funcs.confirmation_code import generate_code
from application.api.funcs.password import verify_password, hash_password
from application.database import db
from application.api.user.models import User, ForgotPassword


class ForgotPasswordEndpoint(MethodResource, Resource):
    forgot_password = reqparse.RequestParser()
    forgot_password.add_argument('email', type=str, required=True)

    @doc(description='Request reset code for change password', tags=['Auth'])
    @use_kwargs(ForgotPasswordPutRequest)
    @marshal_with(ForgotPasswordPutResponse)
    def put(self, *args, **kwargs):
        # Request change password code
        args: dict = self.forgot_password.parse_args()
        email = args['email']

        user_from_db: User = db.session.query(User)\
            .filter(User.email == email, User.enabled == True)\
            .first()
        reset_code = generate_code(6, case='letters+numbers').upper()

        if not user_from_db:
            return {'email_send': 0}

        forgot_password = ForgotPassword(
            user_id=user_from_db.id,
            reset_code=reset_code
        )
        try:
            db.session.add(forgot_password)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return {'email_send': 1}

        resp_status_code = send_email(
            to_email=user_from_db.email,
            content=f'Reset code: {reset_code}'
        )

        return {'email_send': resp_status_code}

    @doc(description='Perform reset code to change password', tags=['Auth'])
    @use_kwargs(ForgotPasswordPostRequest)
    @marshal_with(ForgotPasswordPostResponse)
    def post(self, *args, **kwargs):
        # Perform code

        # check code exists
        forgot_password_model: ForgotPassword = db.session.query(ForgotPassword)\
            .filter(ForgotPassword.reset_code == kwargs.get('reset_code'))\
            .first()

        if not forgot_password_model:
            abort(404, message='Reset code expired or not found')

        if (datetime.utcnow() - forgot_password_model.created_at) > timedelta(hours=1):
            db.session.delete(forgot_password_model)
            db.session.commit()
            abort(404, message='Reset code expired or not found')

        # Get active user
        user = db.session.query(User)\
            .filter(
                User.id == forgot_password_model.user_id,
                User.enabled.is_(True))\
            .first()

        if not user:
            abort(403, message='User blocked')

        if 256 > len(kwargs.get('new_password')) < 8:
            abort(400, message='Password field is too short (8, 256)')

        # clear all reset codes for user:
        forgot_password_requests: List[ForgotPassword] = db.session.query(ForgotPassword)\
            .filter(ForgotPassword.user_id == forgot_password_model.user_id)\
            .all()
        try:
            user.password = hash_password(kwargs.get('new_password'))

            for fg in forgot_password_requests:
                db.session.delete(fg)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            abort(500, message='Problem with update password')

        return {'password_changed': True}


class LoginEndpoint(MethodResource, Resource):
    login_parser = reqparse.RequestParser()
    login_parser.add_argument('email', type=str, required=True)
    login_parser.add_argument('password', type=str, required=True)

    @doc(description='Login endpoint by email/password', tags=['Auth'])
    @use_kwargs(LoginPostEndpointRequest, location='json')
    @marshal_with(LoginPostEndpointResponse)
    def post(self, *args, **kwargs):
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

    @doc(description='Check authorization', tags=['Auth'])
    @jwt_required()
    def get(self):
        """Check auth logic, just check and return"""
        # /api/login/ will return True for authenticated user and 401
        return True


class LogoutEndpoint(MethodResource, Resource):
    @doc(description='Logout endpoint for clear cookies', tags=['Auth'])
    @marshal_with(LogoutGetResponse)
    def get(self):
        response = jsonify({"msg": "logout successful"})
        unset_jwt_cookies(response)
        return response


class RefreshTokenEndpoint(MethodResource, Resource):
    @doc(description='Route for refresh access_token and auth-cookie', tags=['Auth'])
    @marshal_with(RefreshTokenPostEndpointResponse)
    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)

        response = jsonify(access_token=access_token)

        # Also save new access token into cookie for future work with cookie-based session
        set_access_cookies(response, access_token)
        return response
