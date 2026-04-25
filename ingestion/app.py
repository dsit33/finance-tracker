from flask import Flask

from blueprints.health import health_bp

def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)

    if config:
        app.config.update(config)

    app.register_blueprint(health_bp)

    return app

app = create_app()