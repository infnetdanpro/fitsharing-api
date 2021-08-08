from marshmallow import Schema, fields


class OrderResponse(Schema):
    id = fields.Int()
    club_id = fields.Int()
    created_at = fields.Str()
    comment = fields.Str()
    time_to_come = fields.Int()
    confirmation_code = fields.Str()
    price = fields.Float()


class UpdateOrderRequest(Schema):
    order_id = fields.Int(required=True)
    confirm_arrive = fields.Bool()
    end_arrive = fields.Bool()


class GetOrderRequest(Schema):
    order_id = fields.Int(required=True)


class PostOrderRequest(Schema):
    club_id = fields.Int(required=True)
    comment = fields.Str()
    club_service_ids = fields.List(fields.Int())


class DeleteOrderRequest(Schema):
    order_id = fields.Int(required=True)
