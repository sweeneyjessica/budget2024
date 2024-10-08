import os

from flask import Flask
from . import dashboard

UPLOAD_FOLDER = '/Users/jessicasweeney/Documents/budget2024/uploads'

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'budgetapp.sqlite'),
        UPLOAD_FOLDER=UPLOAD_FOLDER
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        app = dashboard.init_dashboard(app)

    # a simple page that says hello
    @app.route('/')
    def hello():
        return 'Hello, World!'
    
    from . import db
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)

    from . import upload
    app.register_blueprint(upload.bp)

    from . import display
    app.register_blueprint(display.bp)
    
    return app
