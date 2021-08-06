from marshmallow import Schema, fields


class LoginPostEndpointResponse(Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()


class LoginPostEndpointRequest(Schema):
    email = fields.Str(default='test@test.com', required=True)
    password = fields.Str(default='test', required=True)


class LogoutGetResponse(Schema):
    msg = fields.Str(default='logout successful')


class ForgotPasswordPutResponse(Schema):
    email_send = fields.Bool()


class ForgotPasswordPutRequest(Schema):
    email = fields.Str(required=True)


class ForgotPasswordPostRequest(Schema):
    reset_code = fields.Str(required=True)
    new_password = fields.Str(required=True)


class ForgotPasswordPostResponse(Schema):
    password_changed = fields.Bool()
