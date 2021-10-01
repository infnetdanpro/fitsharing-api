from marshmallow import fields, Schema


class ClubCheckResponse(Schema):
    club_id = fields.Int()
    club_name = fields.Str()
    price_per_minute = fields.Int()
