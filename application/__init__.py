from datetime import datetime
from datetime import timedelta
from datetime import timezone

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, get_jwt, get_jwt_identity, create_access_token, set_access_cookies, \
    jwt_required
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_restful import Api
from flask_cors import CORS
from jwt import PyJWTError

from application.database import migrate, db
from application.auth.jwt_auth import authenticate, identity
from application.user import models
from application.club import models
from application.order import models


class FixedApi(Api):
  def error_router(self, original_handler, e):
    if not isinstance(e, PyJWTError) and not isinstance(e, JWTExtendedException) and self._has_fr_route():
      try:
        return self.handle_error(e)
      except Exception:
        pass  # Fall through to original handler
    return original_handler(e)


def create_app():
    # FLASK
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    # API
    api = FixedApi(app)
    api.init_app(app)

    # JWT
    # jwt = JWT(app, authenticate, identity)  # Auto Creates /auth endpoint
    jwt = JWTManager(app)

    # DB
    db.init_app(app)
    with app.app_context():
        if db.engine.url.drivername == 'sqlite':
            migrate.init_app(app, db, render_as_batch=True)
        else:
            migrate.init_app(app, db)
    
    # ROUTES
    from application.auth.views import LoginEndpoint, LogoutEndpoint, RefreshTokenEndpoint
    api.add_resource(LoginEndpoint, '/api/login')
    api.add_resource(LogoutEndpoint, '/api/logout')
    api.add_resource(RefreshTokenEndpoint, '/api/refresh')

    from application.user.views import UserEndpoint
    api.add_resource(UserEndpoint, '/api/users')

    from application.club.views import ClubEndpoint, ClubServiceEndpoint, ClubsEndpoint
    api.add_resource(ClubEndpoint, '/api/clubs')
    api.add_resource(ClubsEndpoint, '/api/clubs/all')
    api.add_resource(ClubServiceEndpoint, '/api/clubs/services')


    from application.order.views import OrderEndpoint
    api.add_resource(OrderEndpoint, '/api/orders')

    @app.after_request
    def refresh_expiring_jwts(response):
        try:
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now(timezone.utc)
            target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
            if target_timestamp > exp_timestamp:
                access_token = create_access_token(identity=get_jwt_identity())
                set_access_cookies(response, access_token)
            return response
        except (RuntimeError, KeyError):
            # Case where there is not a valid JWT. Just return the original respone
            return response

    return app
