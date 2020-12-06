import os

from flask import Flask
from flaskr import db
from flaskr.views import bp

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE="classifier/results/spam.db",
    )
    print(app.config["DATABASE"])
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    app.register_blueprint(bp, url_prefix="/")
    return app 
