from flask_restful import Resource, reqparse, abort, fields, marshal_with

from application.database import db
from application.content.models import PublicPage


page_response = {
    'id': fields.Integer,
    'slug': fields.String,
    'title': fields.String,
    'h1': fields.String,
    'body': fields.String,
    'meta_description': fields.String,
    'created_at': fields.DateTime,

}


class PagesEndpoint(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('id', type=int, required=False)
    get_parser.add_argument('slug', type=str, required=False)

    @marshal_with(page_response)
    def get(self):
        args: dict = self.get_parser.parse_args()
        id, slug = args['id'], args['slug']

        if not any([id, slug]):
            abort(404)

        page_query = db.session.query(PublicPage)

        if id:
            page_query = page_query.filter(PublicPage.id == id).first()

        if slug:
            page_query = page_query.filter(PublicPage.slug == slug).first()

        return page_query