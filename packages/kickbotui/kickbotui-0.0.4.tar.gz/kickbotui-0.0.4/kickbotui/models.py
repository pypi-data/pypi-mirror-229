from . import db


class Handlers(db.Model):
    """
    To store commands and timed events.
    """
    id = db.Column(db.Integer, primary_key=True)
    is_command = db.Column(db.Boolean)
    is_reply = db.Column(db.Boolean)
    is_event = db.Column(db.Boolean)
    trigger = db.Column(db.String(100))
    action = db.Column(db.String(300))
    minutes = db.Column(db.Integer, default=0)


class BotSettings(db.Model):
    """
    To store settings for the user-bot.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))

