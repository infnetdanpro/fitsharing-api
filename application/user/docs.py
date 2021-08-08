from marshmallow import Schema, fields


class RegisterPostRequest(Schema):
    firstname = fields.Str(required=True)
    lastname = fields.Str(required=True)
    email = fields.Str(required=True)
    phone = fields.Str(required=True)
    date_of_birth = fields.Str(required=True)
    password = fields.Str(required=True)


class UserResponse(Schema):
    id = fields.Int()
    enabled = fields.Bool()
    username = fields.Str()
    avatar = fields.Str()


class FullUserResponse(Schema):
    id = fields.Int()
    username = fields.Str()
    avatar = fields.Str()
    enabled = fields.Bool()
    firstname = fields.Str()
    lastname = fields.Str()
    phone = fields.Str()
    email = fields.Str()
    date_of_birth = fields.Str()


class UpdateUserRequest(Schema):
    firstname = fields.Str(required=True)
    lastname = fields.Str(required=True)
    phone = fields.Str(required=True)
    date_of_birth = fields.Str(required=True)


class DeleteUserResponse(Schema):
    id = fields.Int()
    enabled = fields.Bool()
