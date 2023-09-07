import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

flask_app = Flask(__name__)
socketio = SocketIO(flask_app, cors_allowed_origins="*", async_mode='gevent')
db = SQLAlchemy()


class BotManager:
    def __init__(self):
        self.bot_running = False
        self.bot_process = None
        self.sent_lines = []
        self.log_filename = os.path.join(os.path.dirname(__file__), 'bot.log')
        self.temp_file = os.path.join(os.path.dirname(__file__), 'tempbot.py')


def create_app():
    """
    Initialize flask app and BotManager
    """
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///bot.db'
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['SECRET_KEY'] = "SuperSecretKey123"
    flask_app.bot_manager = BotManager()
    db.init_app(flask_app)

    from .routing import router
    flask_app.register_blueprint(router, url_prefix='/')

    with flask_app.app_context():
        db.create_all()

    return flask_app



