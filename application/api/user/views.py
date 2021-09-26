import logging
from functools import lru_cache

from flask_apispec import MethodResource, doc, use_kwargs, marshal_with as marshal_with_swagger
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse, abort
from email_validator import validate_email, EmailNotValidError

from application.database import db
from application.api.user.docs import (
    RegisterPostRequest,
    FullUserResponse,
    UpdateUserRequest,
    DeleteUserResponse
)
from application.models.user.models import User, UserBalance
from application.api.funcs.password import hash_password


logger = logging.getLogger('user_views')


@lru_cache()
def email_validator_cached(email):
    try:
        valid = validate_email(email)

        return valid.email
    except EmailNotValidError as e:
        abort(400, message='Bad email')


class UserEndpoint(MethodResource, Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('username', type=str, required=True)
    post_parser.add_argument('firstname', type=str, required=True)
    post_parser.add_argument('password', type=str, required=True)
    post_parser.add_argument('lastname', type=str, required=True)
    post_parser.add_argument('email', type=str, required=True, trim=True)
    post_parser.add_argument('phone', type=str, required=True)
    post_parser.add_argument('date_of_birth', type=str, required=True)

    put_parser = reqparse.RequestParser()
    put_parser.add_argument('id', type=str, required=True)
    put_parser.add_argument('firstname', type=str, required=True)
    put_parser.add_argument('lastname', type=str, required=True)
    put_parser.add_argument('phone', type=str, required=True)
    put_parser.add_argument('date_of_birth', type=str, required=True)

    @doc(description='Get full user info, auth required', tags=['User'])
    @marshal_with_swagger(FullUserResponse)
    @jwt_required()
    def get(self, *args, **kwargs):
        current_user = db.session.query(User).filter(User.email == get_jwt_identity()).one()

        user = db.session.query(User)\
            .filter(User.id == current_user.id, User.enabled.is_(True))\
            .first()

        if not user:
            abort(404, message='User not found')

        return user

    @doc(description='Register user', tags=['User'])
    @use_kwargs(RegisterPostRequest)
    @marshal_with_swagger(FullUserResponse)
    def post(self, *args, **kwargs):
        user = User(**self.post_parser.parse_args())
        if 256 > len(user.password) < 8:
            abort(400, message='Password field is too short (8, 256)')

        user.email = email_validator_cached(user.email)
        user.password = hash_password(user.password)


        try:
            db.session.add(user)
            db.session.flush()
            user_balance = UserBalance(user_id=user.id, amount=0)
            db.session.add(user_balance)
            db.session.commit()
        except IntegrityError:
            abort(409, message='User already exists with this email/username')
            db.session.rollback()
        except Exception as e:
            logger.exception('Something wrong with register new user: %s', e)
            abort(400, message='Something wrong with register new user. Please, try again later')
            db.session.rollback()

        return user

    @doc(description='Update user endpoint', tags=['User'])
    @use_kwargs(UpdateUserRequest)
    @marshal_with_swagger(FullUserResponse)
    @jwt_required()
    def put(self, *args, **kwargs):
        args: dict = self.put_parser.parse_args()
        current_user = db.session.query(User).filter(User.email == get_jwt_identity()).one()

        user = db.session.query(User)\
            .filter(User.id == current_user.id, User.enabled.is_(True))\
            .first()

        if not user:
            abort(404, message='User not found')

        try:
            for field, value in args.items():
                setattr(user, field, value)
            db.session.commit()
        except Exception as e:
            logger.exception('Problem with update user information: %s', str(e))
            abort(400, message='Problem with update user information')
            db.session.rollback()

        return user

    @doc(description='Delete current user (auth required)', tags=['User'])
    @marshal_with_swagger(DeleteUserResponse)
    @jwt_required()
    def delete(self, *args, **kwargs):
        current_user = db.session.query(User).filter(User.email == get_jwt_identity()).one()

        user = db.session.query(User).filter(User.id == current_user.id, User.enabled.is_(True)).first()
        if not user:
            abort(400, message='Problem with getting your user')

        try:
            user.enabled = False
            db.session.commit()
        except Exception as e:
            logger.exception('Problem with delete user: %s', str(e))
            abort(400, message='Problem with delete user')
            db.session.rollback()

        return user
