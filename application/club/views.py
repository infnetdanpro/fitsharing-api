import textwrap
from datetime import datetime, timedelta
from typing import List

from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse, abort, fields, marshal_with

from application.database import db
from application.club.models import Club, ClubService, days_order

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
    get_parser.add_argument('id', type=int, required=True)

    @marshal_with(single_club_response)
    @jwt_required()
    def get(self):
        args: dict = self.get_parser.parse_args()
        club: Club = db.session.query(Club)\
            .filter(Club.enabled == True, Club.id == args['id'])\
            .first()

        if not club:
            abort(404, message='Club not found or disabled')

        club.name = textwrap.shorten(club.name, width=60, placeholder="...")
        club.address = textwrap.shorten(club.address, width=60, placeholder="...")

        # Sort work days
        work_hours_indexes_order = {}
        for work_hour in club.work_hours:
            work_hours_indexes_order[days_order.index(work_hour.day)] = work_hour

        index_order = sorted(work_hours_indexes_order, key=lambda x: x)

        work_hours = []
        for index in index_order:
            work_hours.append(work_hours_indexes_order[index])

        club.work_hours = work_hours

        # Detect open/not open status by week/work hours
        current_datetime = datetime.utcnow() + timedelta(seconds=180*60)    # Moscow +3 hours

        try:
            day = work_hours[current_datetime.weekday()]
        except IndexError:
            # If current week day not exists in work schedule
            return club

        open_time, close_time = day.work_hours.split('-')
        open_hour, open_minute = open_time.split(':')
        close_hour, close_minute = close_time.split(':')

        start_time = current_datetime.replace(hour=int(open_hour), minute=int(open_minute), second=0, microsecond=0)
        end_time = current_datetime.replace(hour=int(close_hour), minute=int(close_minute), second=0, microsecond=0)

        current_datetime = datetime.utcnow() + timedelta(seconds=180*60) # Moscow +3 hours
        setattr(club, 'open', start_time <= current_datetime <= end_time)
        return club


class ClubServiceEndpoint(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('club_id', type=int, required=True)

    @jwt_required()
    def get(self):
        args = self.get_parser.parse_args()
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

    @marshal_with(list_clubs_response)
    @jwt_required()
    def get(self):
        args = self.get_parser.parse_args()

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
