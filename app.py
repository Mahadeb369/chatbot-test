import os
from flask import Flask
from application.config import LocalDevelopmentConfig

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

PORT = os.getenv("PORT") or ""

# SQLAlchemy setup
db = SQLAlchemy(engine_options={"pool_size": 10, "pool_recycle": 1800, "pool_pre_ping": True})


current_dir = os.path.abspath(os.path.dirname(__file__))

app = None

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(LocalDevelopmentConfig)

    # Initialize SQLAlchemy with the Flask app
    db.init_app(app)

    app.app_context().push()
    return app

app = create_app()

migrate = Migrate(app, db)

from application.controllers import *
from chatbot_api.controllers import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
