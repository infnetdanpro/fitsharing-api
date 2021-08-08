from datetime import datetime
from typing import List

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse, abort, fields, marshal_with

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
class OrderEndpoint(Resource):
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

    @marshal_with(single_order_response)
    @jwt_required()
    def get(self):
        # get info about order
        args: dict = self.get_args.parse_args()
        current_user = get_jwt_identity()
        order = db.session.query(Order)\
            .filter(Order.id == args['order_id'], Order.user_id == current_user.id)\
            .first()
        
        if not order:
            abort(404, message=f'Order with id: {args["order_id"]} is not found')

        return order

    @marshal_with(single_order_response)
    @jwt_required()
    def post(self):
        # create order
        args: dict = self.post_args.parse_args()
        current_user = get_jwt_identity()

        club_service_ids: List[int] = args.get('club_service_ids')
        # We don't need this check because ParserArgument already do this
        # for club_service_id in club_service_ids:
        #     if not isinstance(club_service_id, int):
        #         abort(400, message='Club services ids must be all integers ([1, 2])')

        user_id = current_user.id
        choiced_club_services = db.session\
            .query(ClubService)\
            .filter(ClubService.id.in_(club_service_ids), ClubService.enabled.is_(True))
        
        if len(club_service_ids) != choiced_club_services.count():
            abort(404, message='One of club_service_id not found')

        price = 0
        for club_service in choiced_club_services.all():
            price += club_service.price

        try:
            new_order = Order(
                user_id=user_id,
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

            for club_service in choiced_club_services.all():
                new_ordered_service = OrderService(order=new_order, club_service=club_service)
                db.session.add(new_ordered_service)

            db.session.commit()
            return new_order
        except Exception as e:
            db.session.rollback()
            abort(400, message=f'Error creating order: {e}')

    def put(self):
        # update order by client
        pass

    def delete(self):
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
            return {'id': order_id, 'canceled': True}
        except Exception as e:
            db.session.rollback()
            abort(422, message=f'Can not cancel order: {order_id}.')
