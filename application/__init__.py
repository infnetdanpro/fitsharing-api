from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask
from flask_apispec import FlaskApiSpec
from flask_jwt_extended import JWTManager, get_jwt, get_jwt_identity, create_access_token, set_access_cookies
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_login import LoginManager
from flask_restful import Api
from jwt import PyJWTError

import sentry_sdk

from application import config

sentry_sdk.init(
    config.SENTRY_DSN,
    environment=config.FLASK_ENV,
    traces_sample_rate=1.0
)

from application.database import *
from application.models.user.models import *
from application.models.club.models import *
from application.models.order.models import *
from application.models.content.models import *
from application.models.club_user.models import *
from application.models.role.models import *
from application.models.notifications.models import *
from application.models.payment.models import *


from flask_admin import Admin

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

    admin = Admin(app, name='admin', template_mode='bootstrap3')

    # API
    api = FixedApi(app)
    api.init_app(app)

    club_login_manager = LoginManager()
    club_login_manager.init_app(app)

    @club_login_manager.user_loader
    def load_user(user_id):
        return db.session.query(ClubUser).get(user_id)

    from application.club_admin import bp as bp_route
    app.register_blueprint(bp_route, url_prefix='/club-panel')

    from application.payment import bp as pay_route
    app.register_blueprint(pay_route, url_prefix='/payment')

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
    from application.api.auth.views import LoginEndpoint, LogoutEndpoint, RefreshTokenEndpoint, ForgotPasswordEndpoint
    api.add_resource(LoginEndpoint, '/api/login')
    api.add_resource(LogoutEndpoint, '/api/logout')
    api.add_resource(ForgotPasswordEndpoint, '/api/forgot-password')
    api.add_resource(RefreshTokenEndpoint, '/api/refresh')

    from application.api.user.views import UserEndpoint
    api.add_resource(UserEndpoint, '/api/users')

    from application.api.club.views import ClubEndpoint, ClubServiceEndpoint, ClubsEndpoint, ClubCheckEndpoint
    api.add_resource(ClubEndpoint, '/api/clubs')
    api.add_resource(ClubsEndpoint, '/api/clubs/all')
    api.add_resource(ClubCheckEndpoint, '/api/clubs/check')
    api.add_resource(ClubServiceEndpoint, '/api/clubs/services')

    from application.api.order.views import OrderEndpoint, OrderHistoryEndpoint
    api.add_resource(OrderEndpoint, '/api/orders')
    api.add_resource(OrderHistoryEndpoint, '/api/orders/history')

    from application.api.content.views import PagesEndpoint
    api.add_resource(PagesEndpoint, '/api/page')

    @app.after_request
    def refresh_expiring_jwts(response):
        try:
            import datetime
            exp_timestamp = get_jwt()["exp"]
            now = datetime.datetime.now(tz=datetime.timezone.utc)
            target_timestamp = datetime.datetime.timestamp(now + datetime.timedelta(minutes=30))
            if target_timestamp > exp_timestamp:
                access_token = create_access_token(identity=get_jwt_identity())
                set_access_cookies(response, access_token)
            return response
        except (RuntimeError, KeyError):
            # Case where there is not a valid JWT. Just return the original response
            return response

    # Docs:
    app.config.update({
        'APISPEC_SPEC': APISpec(
            title='FitSharing API DOCS',
            version='v1',
            plugins=[MarshmallowPlugin()],
            openapi_version='2.0.0'
        ),
        'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
        'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
    })
    docs = FlaskApiSpec(app)

    docs.register(LoginEndpoint)
    docs.register(LogoutEndpoint)
    docs.register(ForgotPasswordEndpoint)
    docs.register(RefreshTokenEndpoint)
    docs.register(UserEndpoint)
    docs.register(OrderEndpoint)
    docs.register(OrderHistoryEndpoint)
    docs.register(ClubCheckEndpoint)

    return app
