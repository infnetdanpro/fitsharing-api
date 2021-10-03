from marshmallow import fields, Schema


class ClubRequest(Schema):
    club_id = fields.Int()
    id = fields.Int()


class ClubCheckResponse(Schema):
    club_id = fields.Int()
    club_name = fields.Str()
    price_per_minute = fields.Int()
