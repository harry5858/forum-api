from flask import Flask
from flask_jwt_extended import JWTManager
from .config.config import config

jwt = JWTManager()

def create_app(config_name = 'testing'):

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    from forum import db

    db.init_app2(app)

    jwt.init_app(app)

    # Register Blueprint here
    from .feature_auth import auth
    app.register_blueprint(auth.auth)

    from .feature_post import post
    app.register_blueprint(post.post)

    # Custom token expired response
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, kwy_payload):
        return {'msg': "Token expired."}, 401

    return app


