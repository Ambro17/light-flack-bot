from flask import Flask


def create_app():
    app = Flask(__name__)
    #app.config.from_object(config[config_name])

    # Register web application routes
    from api import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Register async tasks support
    from tasks import tasks_bp as tasks_blueprint
    app.register_blueprint(tasks_blueprint, url_prefix='/tasks')

    # Register async tasks support
    from interactivity import bp as interactive_blueprint
    app.register_blueprint(interactive_blueprint, url_prefix='/interactive')

    return app