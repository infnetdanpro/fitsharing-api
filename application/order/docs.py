from marshmallow import Schema, fields


class OrderResponse(Schema):
    id = fields.Int()
    club_id = fields.Int()
    user_id = fields.Int()
    created_at = fields.Str()
    updated_at = fields.Str()
    comment = fields.Str()
    price = fields.Float()
    time_to_come = fields.Int()
    confirmation_code = fields.Str()

    # arrived client and confirm by club
    client_arrived_at = fields.Str()
    club_confirmed_client_arrived_at = fields.Str()

    # End arrive by user and confirm by club
    client_completed_at = fields.Str()
    club_confirmed_client_completed_at = fields.Str()

    # Cancel order by client/by club
    client_canceled_at = fields.Str()
    club_canceled_at = fields.Str()

    complete = fields.Bool()
    minutes = fields.Int()


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
