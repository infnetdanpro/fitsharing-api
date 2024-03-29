from datetime import datetime
from typing import List

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse, abort, fields
from flask_apispec import MethodResource, marshal_with as marshal_with_swagger, doc, use_kwargs
from sqlalchemy import desc

from application.api.order.docs import (
    OrderResponse,
    UpdateOrderRequest,
    PostOrderRequest,
    ListOrderResponse
)
from application.models.order.models import Order
from application.database import db
from application.api.funcs.confirmation_code import generate_code
from application.models.user.models import User, UserBalance
from application.models.club.models import Club

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
        code = generate_code(case='letters+numbers').upper()
        exists = db.session\
            .query(Order)\
            .filter(Order.confirmation_code == code)\
            .count()
        if not exists:
            return code


class OrderEndpoint(MethodResource, Resource):
    """For single order"""
    get_args = reqparse.RequestParser()
    get_args.add_argument('order_id', type=int, required=True)

    post_args = reqparse.RequestParser()
    # post_args.add_argument('user_id', type=int, required=False)
    post_args.add_argument('club_id', type=int, required=True)
    post_args.add_argument('is_qr', type=bool, required=False)
    post_args.add_argument('comment', type=str, required=False)
    post_args.add_argument('club_service_ids', type=int, action='append')

    delete_args = reqparse.RequestParser()
    delete_args.add_argument('order_id', type=int, required=True)
    # delete_args.add_argument('user_id', type=int, required=False)

    put_args = reqparse.RequestParser()
    put_args.add_argument('order_id', type=int, required=True)
    put_args.add_argument('is_qr', type=bool, required=False)
    put_args.add_argument('confirm_arrive', type=bool, required=False)
    put_args.add_argument('end_arrive', type=bool, required=False)

    @doc(description='Get single order info by `order_id`', tags=['Order'])
    @marshal_with_swagger(OrderResponse)
    # @use_kwargs(GetOrderRequest)
    @jwt_required()
    def get(self, *args, **kwargs):
        # get info about order
        args: dict = self.get_args.parse_args()
        current_user = db.session.query(User).filter(User.email == get_jwt_identity()).one()
        order = db.session.query(Order)\
            .filter(Order.id == args['order_id'], Order.user_id == current_user.id)\
            .first()

        if not order:
            abort(404, message=f'Order with id: {args["order_id"]} is not found')


        if order.client_arrived_at:
            setattr(order, 'minutes', (datetime.utcnow() - order.client_arrived_at).seconds // 60)
        elif order.is_qr:
            setattr(order, 'minutes', (datetime.utcnow() - order.created_at).seconds // 60)
        else:
            setattr(order, 'minutes', 0)
        return order

    @doc(description='Create order', tags=['Order'])
    @use_kwargs(PostOrderRequest)
    # @marshal_with_swagger(OrderResponse)
    @jwt_required()
    def post(self, *args, **kwargs):
        # create order
        args: dict = self.post_args.parse_args()
        current_user: User = db.session.query(User).filter(User.email == get_jwt_identity()).one()

        if not current_user.balance or current_user.balance.amount < 100:
            UserBalance.update(user_id=current_user.id, amount=0)
            abort(400, message='У вас недостаточно денег для посещения! (необходимо минимум 100 рублей на счету)')

        # Check already exists orders
        uncompleted_orders = db.session.query(Order).filter(
            Order.user_id == current_user.id,
            Order.complete.is_(False)
        ).all()

        if uncompleted_orders:
            abort(409, message='У вас есть незавершенные посещения')

        # club_service_ids: List[int] = args.get('club_service_ids')
        # We don't need this check because ParserArgument already do this
        # for club_service_id in club_service_ids:
        #     if not isinstance(club_service_id, int):
        #         abort(400, message='Club services ids must be all integers ([1, 2])')

        price = 0

        # if club_service_ids:
        #     choice_club_services = db.session\
        #         .query(ClubService)\
        #         .filter(ClubService.id.in_(club_service_ids), ClubService.enabled.is_(True))\
        #         .all()
        #
        #     for club_service in choice_club_services:
        #         if club_service.service_type == 'main':
        #             continue
        #         price += club_service.price

        club: Club = db.session.query(Club).filter(Club.id == args['club_id'], Club.enabled.is_(True)).first()
        if not club:
            abort(400, message='Извините, данный клуб отключен!')

        max_minutes = current_user.balance.amount // int(club.get_price_per_minute())

        if args.get('is_qr'):
            dt_now = datetime.utcnow()
            new_order = Order(
                user_id=current_user.id,
                club_id=args['club_id'],
                price=price,
                is_qr=True,
                client_arrived_at=dt_now,
                club_confirmed_client_arrived_at=dt_now,     # autoconfirm for is_qr
                max_minutes=max_minutes
            )
        else:
            new_order = Order(
                user_id=current_user.id,
                created_at=datetime.utcnow(),
                club_id=args['club_id'],
                comment=args.get('comment'),
                price=price,
                time_to_come=60,    # todo: get from settings
                confirmation_code=get_unique_confirmation_code(),
                max_minutes=max_minutes
            )
        try:
            db.session.add(new_order)
            db.session.commit()
            resp = {
                'id': new_order.id,
                'club_name': club.name,
                'club_id': new_order.club_id,
                'created_at': new_order.created_at,
                'price_per_minute': club.get_price_per_minute(),
                'text_created_at': new_order.created_at.strftime('%d.%m.%Y %H:%M'),
                'max_minutes': new_order.max_minutes
            }
            return resp
        except Exception as e:
            db.session.rollback()
            abort(400, message=f'Ошибка на сервере, код ошибки: #ORDER81812')

    @doc(description='Update order (confirm or end)', tags=['Order'])
    # @use_kwargs(UpdateOrderRequest)
    @marshal_with_swagger(OrderResponse)
    @jwt_required()
    def patch(self, *args, **kwargs):
        args: dict = self.put_args.parse_args()
        current_user = db.session.query(User).filter(User.email == get_jwt_identity()).one()

        # update order by client
        order: Order = db.session.query(Order)\
            .filter(
                Order.user_id == current_user.id,
                Order.id == args['order_id'],
                Order.complete.is_(False),
                Order.client_canceled_at.is_(None),
                Order.club_canceled_at.is_(None))\
            .first()

        if not order:
            abort(404, message='Посещение завершено или отменено, обратитесь в поддержку')

        # if not any([args['confirm_arrive'], args['end_arrive']]):
        #     abort(400, message='Нехватает информации для получения заказа')

        if args['is_qr']:
            order.complete = True
            order.client_completed_at = datetime.utcnow()
            price_per_minute = order.club.get_price_per_minute()

            minutes = (order.client_completed_at - order.created_at).seconds // 60
            remain = (order.client_completed_at - order.created_at).seconds % 60

            if minutes < 1:
                minutes = 1

            if minutes > 1 and remain > 30:
                # округляем в большую сторону :)
                minutes += 1

            order.price = minutes * price_per_minute

            result = False

            try:
                result = True
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                abort(400, message='Проблема с завершением заказа')

            if result:
                UserBalance.update(user_id=order.user_id, amount=-order.price)

            return order

        if args['confirm_arrive']:
            # TODO: add here some action for trigger in CMS/Web for Clubs!
            # TODO: club need to confirm arrive (order.confirmed_club)
            order.client_arrived_at = datetime.utcnow()
            db.session.commit()
            return order

        if args['end_arrive']:
            # Complete order
            # TODO: confirm client logic
            order.complete = True
            order.client_completed_at = datetime.utcnow()
            price_per_minute = order.club.get_price_per_minute()
            total_price = (order.client_completed_at - order.client_arrived_at).seconds // 60 * price_per_minute
            order.price = total_price

            result = False
            try:
                result = True
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                abort(400, message='Problem with finish order!')

            if result:
                UserBalance.update(user_id=order.user_id, amount=-order.price)

            return order

    @doc(description='Cancel order', tags=['Order'])
    # @use_kwargs(DeleteOrderRequest)
    @marshal_with_swagger(OrderResponse)
    @jwt_required()
    def delete(self, *args, **kwargs):
        # cancel order
        args: dict = self.delete_args.parse_args()
        current_user = db.session.query(User).filter(User.email == get_jwt_identity()).one()

        order: Order = db.session\
            .query(Order)\
            .filter(
            Order.id == args['order_id'],
            Order.user_id == current_user.id,
            Order.client_canceled_at.is_(None),
            Order.club_canceled_at.is_(None)
        ).first()

        if not order:
            abort(404, message='Order not found or already canceled/deleted')

        try:
            order.canceled_by_client = True
            order.is_active = False
            order.complete = False
            db.session.commit()
            return order
        except Exception as e:
            db.session.rollback()
            abort(422, message=f'Can not cancel order: {args["order_id"]}.')


class OrderHistoryEndpoint(MethodResource, Resource):
    get_args = reqparse.RequestParser()
    get_args.add_argument('limit', type=int, default=10)
    get_args.add_argument('offset', type=int, default=0)

    @doc(description='History of orders, auth required', tags=['Order'])
    @marshal_with_swagger(ListOrderResponse)
    @jwt_required()
    def get(self, *args, **kwargs):
        args: dict = self.get_args.parse_args()
        current_user = db.session.query(User).filter(User.email == get_jwt_identity()).one()

        orders: List[Order] = db.session\
            .query(Order)\
            .filter(Order.user_id == current_user.id)\
            .order_by(desc(Order.created_at))\
            .limit(args['limit'])\
            .offset(args['offset'])\
            .all()

        return {'orders': orders, 'limit': args['limit'], 'offset': args['offset']}
