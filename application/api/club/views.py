import textwrap
import uuid
from datetime import datetime, timedelta
from typing import List

from flask_apispec import MethodResource, doc, marshal_with as marshal_with_swagger, use_kwargs
from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse, abort, fields, marshal_with

from application.api.club.docs import ClubCheckResponse, ClubRequest
from application.database import db
from application.models.club.models import Club, ClubService, days_order

images_club_response = {
    'name': fields.String,
    'image': fields.String,
    'sequence': fields.Integer,
    'created_at': fields.DateTime
}


service_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'about': fields.String
}

work_hours_fields = {
    'id': fields.Integer,
    'day': fields.String,
    'work_hours': fields.String
}


single_club_response = {
    'id': fields.Integer,
    'name': fields.String,
    'address': fields.String,
    'phone': fields.String,
    'lat': fields.Float,
    'lng': fields.Float,
    'about': fields.String,
    'images': fields.List(fields.Nested(images_club_response)),
    'work_hours': fields.List(fields.Nested(work_hours_fields)),
    'open': fields.Boolean(default=False),
}


club_services_response = {
    'club_id': fields.Integer,
    'services': fields.List(fields.Nested(service_fields), attribute="items")
}


class ClubEndpoint(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('club_id', type=int, required=False)
    get_parser.add_argument('id', type=int, required=True)

    # @doc(description='Get club info', tags=['Clubs'])
    # @marshal_with(single_club_response)
    @jwt_required()
    def get(self):
        args: dict = self.get_parser.parse_args()
        club: Club = db.session.query(Club)\
            .filter(Club.enabled.is_(True), Club.id == args['id'])\
            .first()

        if not club:
            abort(404, message='Club not found or disabled')

        club.name = textwrap.shorten(club.name, width=60, placeholder="...")
        club.address = textwrap.shorten(club.address, width=60, placeholder="...")

        # Sort work days
        work_hours_indexes_order = {}
        for work_hour in club.work_hours:
            work_hours_indexes_order[days_order.index(work_hour.day)] = {
                'id': work_hour.id,
                'day': work_hour.day,
                'work_hours': work_hour.work_hours
            }

        index_order = sorted(work_hours_indexes_order, key=lambda x: x)

        work_hours = []
        for index in index_order:
            work_hours.append(work_hours_indexes_order[index])

        # Detect open/not open status by week/work hours
        current_datetime = datetime.utcnow() + timedelta(seconds=180*60)    # Moscow +3 hours

        try:
            day = work_hours[current_datetime.weekday()]
        except IndexError:
            # If current week day not exists in work schedule
            day = {}

        open_time, close_time = day['work_hours'].split('-') if day.get('work_hours') else '00:00', '23:59'
        open_hour, open_minute = open_time.split(':')
        close_hour, close_minute = close_time.split(':')

        start_time = current_datetime.replace(hour=int(open_hour), minute=int(open_minute), second=0, microsecond=0)
        end_time = current_datetime.replace(hour=int(close_hour), minute=int(close_minute), second=0, microsecond=0)

        current_datetime = datetime.utcnow() + timedelta(seconds=180*60) # Moscow +3 hours
        setattr(club, 'open', start_time <= current_datetime <= end_time)

        club_services: List[ClubService] = db.session.query(ClubService) \
            .filter(ClubService.club_id == club.id) \
            .all()

        services = []

        if club_services:
            for cs in club_services:
                services.append({
                    'id': cs.service.id,
                    'name': cs.service.name,
                    'about': cs.service.about,
                    'price': cs.price,
                    'service_type': cs.service_type
                })

        images = []

        # name = db.Column(db.String)
        # image = db.Column(db.String)
        # sequence = db.Column(db.Integer, default=0)
        # club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
        # created_at
        for image in club.images:
            images.append({
                'name': image.name,
                'image': image.image,
                'sequence': image.sequence
            })

        images = sorted(images, key=lambda i: i['sequence'])

        club_info = {
            'id': club.id,
            'name': club.name,
            'address': club.address,
            'phone': club.phone,
            'lat': club.lat,
            'lng': club.lng,
            'about': club.about,
            'images': images,
            'work_hours': work_hours,
            'open': club.open,
            'services': services
        }

        return club_info


class ClubServiceEndpoint(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('club_id', type=int, required=True)

    @doc(description='List club services for single club', tags=['Clubs'])
    @use_kwargs(ClubRequest)
    @jwt_required()
    def get(self):
        args: dict = self.get_parser.parse_args()
        club_services: List[ClubService] = db.session.query(ClubService)\
            .filter(ClubService.club_id == args['club_id'])\
            .all()
        
        if not club_services:
            abort(404, messages=f'No services for this club: {args["club_id"]}')

        resp = {'club_id': args['club_id']}

        services = []
        for cs in club_services:
            services.append({
                'id': cs.service.id,
                'name': cs.service.name,
                'about': cs.service.about,
                'price': cs.price,
                'service_type': cs.service_type
            })
        resp.update({'services': services})
        return resp


coordinates_response = {
    'type': fields.String,
    'coordinates': fields.List(fields.Float)
}


club_response = {
    'id': fields.Integer,
    'name': fields.String,
    'address': fields.String,
    'phone': fields.String,
    'gps': fields.Nested(coordinates_response),
    'dist': fields.Float
}

list_clubs_response = {
    'records': fields.List(fields.Nested(club_response)),
}


class ClubsEndpoint(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('lng', type=float, required=False)
    get_parser.add_argument('lat', type=float, required=False)
    get_parser.add_argument('limit', type=int, required=False, default=10)
    get_parser.add_argument('offset', type=int, required=False, default=0)

    @doc(description='List clubs for map', tags=['Clubs'])
    @marshal_with(list_clubs_response)
    @jwt_required()
    def get(self):
        args: dict = self.get_parser.parse_args()

        if args['lng'] and args['lat']:
            # add gps position of user
            clubs_result = db.session.execute("""
                WITH subq AS (
                  SELECT 
                    id, 
                    name, 
                    ST_AsGeoJSON(point)::json AS gps, 
                    address, 
                    phone,
                    ST_DistanceSphere(point, ST_GeomFromEWKT('SRID=4326;POINT(:lng :lat)')) AS dist
                  FROM club
                  WHERE club.enabled IS TRUE
                  ORDER BY point <-> ST_GeomFromEWKT('SRID=4326;POINT(:lat :lng)')
                  LIMIT :limit OFFSET :offset
                ) SELECT * FROM subq ORDER BY dist;
            """, params=args)
            clubs_results = clubs_result.fetchall()
        else:
            query = """
                SELECT 
                    id, 
                    name, 
                    ST_AsGeoJSON(point)::json AS gps, 
                    address, 
                    phone
                FROM club
                WHERE club.enabled IS TRUE
                ORDER BY id DESC
                LIMIT :limit
                OFFSET :offset
            """
            clubs_results = db.session.execute(query, args).fetchall()

        return {'records': clubs_results}, 200


class ClubCheckEndpoint(MethodResource, Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('club_uuid', type=str, required=True)

    @doc(description='Check club by uuid4', tags=['Clubs'])
    @marshal_with_swagger(ClubCheckResponse)
    @jwt_required()
    def get(self):
        args: dict = self.get_parser.parse_args()

        app_name, club_uuid = None, None
        try:
            get_data = args['club_uuid'].split('_')
            app_name, club_uuid = get_data

            if app_name.lower() != 'fitsharing':
                abort(403)
        except:
            abort(400, message='Код нераспознан')

        try:
            uuid.UUID(club_uuid)
        except ValueError:
            abort(422, message='Невалидный идентификатор клуба')

        club = db.session.query(Club)\
            .filter(Club.club_uuid == club_uuid, Club.enabled.is_(True))\
            .first()

        if not club:
            abort(404, message='Клуб не найден или отключен в данный момент')

        price_per_minute = club.get_price_per_minute()

        if price_per_minute <= 0:
            abort(402, message='В клубе не выставлена стоимость посещения, '
                               'вы не можете посетить данный клуб. Обратитесь к администратору')

        return {'club_id': club.id, 'club_name': club.name, 'price_per_minute': price_per_minute}
