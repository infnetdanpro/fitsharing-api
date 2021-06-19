from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse, abort, fields, marshal_with

from application.database import db
from application.user.models import User
from application.funcs.password import hash_password

user_response = {
    'id': fields.Integer,
    'enabled': fields.Boolean,
    'username': fields.String,
    'avatar': fields.String
}

full_user_response = {
    **user_response,
    'enabled': fields.Boolean,
    'firstname': fields.String,
    'lastname': fields.String,
    'phone': fields.String,
    'email': fields.String,
    'date_of_birth': fields.String
}

success_delete_response = {
    'id': fields.Integer,
    'enabled': fields.Boolean
}


class UserEndpoint(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('id', type=int, required=False)

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

    delete_parser = reqparse.RequestParser()
    delete_parser.add_argument('id', type=str, required=True)

    @marshal_with(full_user_response)
    @jwt_required()
    def get(self):
        args = self.get_parser.parse_args()
        current_user = get_jwt_identity()

        if current_user.id != args['id']:
            abort(403, message='Access denied')

        user = db.session.query(User).filter(User.id == args['id'], User.enabled == True).first()

        if not user:
            abort(404, message='User not found')

        return user

    @marshal_with(full_user_response)
    def post(self):
        user = User(**self.post_parser.parse_args())
        if 256 > len(user.password) < 8:
            abort(400, message='Password field is too short (8, 256)')

        user.password = hash_password(user.password)

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            abort(409, message='User already exists')
            db.session.rollback()

        return user

    @marshal_with(full_user_response)
    @jwt_required()
    def put(self):
        args = self.put_parser.parse_args()
        current_user = get_jwt_identity()

        if current_user.id != args['id']:
            abort(403, message='Access denied')

        user = db.session.query(User).filter(User.id == args['id'], User.enabled == True).first()

        if not user:
            abort(404, message='User not found')

        for field, value in args.items():
            if field != 'id':
                setattr(user, field, value)

        db.session.commit()

        return user

    @marshal_with(success_delete_response)
    @jwt_required()
    def delete(self):
        args = self.delete_parser.parse_args()
        current_user = get_jwt_identity()

        if current_user.id != args['id']:
            abort(403, message='Access denied')

        user = db.session.query(User).filter(User.id == args['id'], User.enabled == True).first()
        user.enabled = 0
        db.session.commit()

        return user
