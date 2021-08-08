from datetime import datetime
from typing import List

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from flask_apispec import MethodResource, marshal_with as marshal_with_swagger, doc, use_kwargs

from application.order.docs import OrderResponse, UpdateOrderRequest, PostOrderRequest, DeleteOrderRequest, \
    GetOrderRequest
from application.order.models import Order, OrderService
from application.club.models import ClubService
from application.database import db
from application.funcs.confirmation_code import generate_code


single_order_response = {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'club_id': fields.Integer,
    'created_at': fields.String,
    'comment': fields.String,
    'time_to_come': fields.Integer,
    'price': fields.Float
}

canceled_order_response = {
    'id': fields.Integer,
    'canceled': fields.Boolean
}


def get_unique_confirmation_code():
    """may be it will be very slow operation"""
    # TODO: optimize it!
    while True:
        code = generate_code()
        exists = db.session\
            .query(Order)\
            .filter(Order.confirmation_code == code, Order.confirmed_client == 0)\
            .count()
        if not exists:
            return code


# For single order
class OrderEndpoint(MethodResource, Resource):
    get_args = reqparse.RequestParser()
    get_args.add_argument('order_id', type=int, required=True)

    post_args = reqparse.RequestParser()
    # post_args.add_argument('user_id', type=int, required=False)
    post_args.add_argument('club_id', type=int, required=True)
    post_args.add_argument('comment', type=str, required=False)
    post_args.add_argument('club_service_ids', type=int, action='append')

    delete_args = reqparse.RequestParser()
    delete_args.add_argument('order_id', type=int, required=True)
    # delete_args.add_argument('user_id', type=int, required=False)

    put_args = reqparse.RequestParser()
    put_args.add_argument('order_id', type=int, required=True)
    put_args.add_argument('confirm_arrive', type=bool, required=False)
    put_args.add_argument('end_arrive', type=bool, required=False)

    @doc(description='Get single order info by `order_id`', tags=['Order'])
    @use_kwargs(GetOrderRequest)
    @marshal_with_swagger(OrderResponse)
    @jwt_required()
    def get(self, *args, **kwargs):
        # get info about order
        args: dict = self.get_args.parse_args()
        current_user = get_jwt_identity()
        order = db.session.query(Order)\
            .filter(Order.id == args['order_id'], Order.user_id == current_user.id)\
            .first()

        if not order:
            abort(404, message=f'Order with id: {args["order_id"]} is not found')

        return order

    @doc(description='Create order', tags=['Order'])
    @use_kwargs(PostOrderRequest)
    @marshal_with_swagger(OrderResponse)
    @jwt_required()
    def post(self, *args, **kwargs):
        # create order
        args: dict = self.post_args.parse_args()
        current_user = get_jwt_identity()

        club_service_ids: List[int] = args.get('club_service_ids')
        # We don't need this check because ParserArgument already do this
        # for club_service_id in club_service_ids:
        #     if not isinstance(club_service_id, int):
        #         abort(400, message='Club services ids must be all integers ([1, 2])')

        choice_club_services = db.session\
            .query(ClubService)\
            .filter(ClubService.id.in_(club_service_ids), ClubService.enabled.is_(True))

        if len(club_service_ids) != choice_club_services.count():
            abort(404, message='One of club_service_id not found')

        price = 0
        for club_service in choice_club_services.all():
            if club_service.service_type == 'main':
                continue
            price += club_service.price

        try:
            new_order = Order(
                user_id=current_user.id,
                created_at=datetime.utcnow(),
                club_id=args['club_id'],
                comment=args.get('comment'),
                price=price,
                time_to_come=60,    # todo: get from settings
                confirmation_code=get_unique_confirmation_code(),
                is_active=True
            )

            db.session.add(new_order)
            db.session.flush()

            for club_service in choice_club_services.all():
                new_ordered_service = OrderService(order=new_order, club_service=club_service)
                db.session.add(new_ordered_service)

            db.session.commit()
            return new_order
        except Exception as e:
            db.session.rollback()
            abort(400, message=f'Error creating order: {e}')

    @doc(description='Update order (confirm or end)', tags=['Order'])
    @use_kwargs(UpdateOrderRequest)
    @marshal_with_swagger(OrderResponse)
    @jwt_required()
    def put(self, *args, **kwargs):
        args: dict = self.put_args.parse_args()
        current_user = get_jwt_identity()

        # update order by client
        order: Order = db.session.query(Order)\
            .filter(
                Order.user_id == current_user.id,
                Order.id == args['order_id'],
                Order.is_active.is_(True),
                Order.canceled_by_client.is_(False),
                Order.canceled_by_club.is_(False))\
            .first()

        if not order:
            abort(404, message='Order is not active or deleted, check order information')

        if not any([args['confirm_arrive'], args['end_arrive']]):
            abort(400, message='end_arrive or confirm_arrive is required')

        if args['confirm_arrive']:
            # TODO: add here some action for trigger in CMS/Web for Clubs!
            # TODO: club need to confirm arrive (order.confirmed_club)
            order.confirmed_client = True
            order.confirmed_at = datetime.utcnow()
            db.session.commit()
            return order

        if args['end_arrive']:
            # Complete order
            # Calculate full price
            order.complete = True
            order.completed_at = datetime.utcnow()
            # get price of arrive per minute
            price_per_minute = order.club.get_price_per_minute()
            total_price = (order.completed_at - order.confirmed_at).seconds // 60 * price_per_minute
            order.price = total_price
            db.session.commit()
            return order

    @doc(description='Cancel order', tags=['Order'])
    @use_kwargs(DeleteOrderRequest)
    @marshal_with_swagger(OrderResponse)
    @jwt_required()
    def delete(self, *args, **kwargs):
        # cancel order
        args: dict = self.delete_args.parse_args()
        order_id = args['order_id']
        current_user = get_jwt_identity()

        order: Order = db.session\
            .query(Order)\
            .filter(Order.id == order_id, Order.user_id == current_user.id)\
            .first()

        if not order:
            abort(404, message='Order not found')

        try:
            order.canceled_by_client = True
            order.is_active = False
            db.session.commit()
            return order
        except Exception as e:
            db.session.rollback()
            abort(422, message=f'Can not cancel order: {order_id}.')
