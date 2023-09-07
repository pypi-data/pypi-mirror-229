import threading
import html

from kickbot import KickBot
from flask import (
    request,
    flash,
    redirect,
    url_for,
    render_template,
    Blueprint
)

from . import db, flask_app
from .bot_functions import run_bot, send_bot_output
from .models import Handlers, BotSettings

router = Blueprint('router', __name__)


@router.route('/', methods=['GET', 'POST'])
def home_page():
    """
    Main Dashboard page.
    On post, launch thread to run bot and a thread to send output back to dashboard over socket.
    """
    if request.method == 'POST':
        if flask_app.bot_manager.bot_running:
            flash("Bot already running.", category='success')
            return redirect(url_for('router.home_page'))

        streamer_name = request.form.get('streamer_name')
        bot = BotSettings.query.first()
        if not bot:
            flash("No bot setup yet.", category='error')
            return redirect(url_for('router.home_page'))
        username = bot.username
        password = bot.password
        bot_thread = threading.Thread(target=run_bot, args=(streamer_name, username, password))
        bot_thread.start()
        output_thread = threading.Thread(target=send_bot_output)
        output_thread.start()
        flash("Bot is starting...", category='success')
        return redirect(url_for('router.home_page'))

    flask_app.bot_manager.sent_lines = []
    return render_template('dashboard.html', bot_running=flask_app.bot_manager.bot_running)


@router.route('/commands', methods=['GET', 'POST'])
def commands_page():
    """
    Page to view and add commands.
    """
    if request.method == 'POST':
        prefix = request.form.get('prefix')
        command = request.form.get('command')
        action = request.form.get('command_action')
        response = request.form.get('action_response')
        if any(value is None for value in [prefix, command, action, response]):
            flash("Invalid form. All fields are required.", category='error')
            return redirect(url_for('router.commands_page'))

        full_command = prefix + command
        already_command = Handlers.query.filter_by(trigger=full_command).first()
        if already_command:
            flash("There is already a handler for that command.", category='error')
            return redirect(url_for('router.commands_page'))

        is_reply = True if action == 'reply' else False
        new_command = Handlers(is_command=True, is_reply=is_reply, trigger=full_command, action=response)
        db.session.add(new_command)
        db.session.commit()
        flash("Command Added.", category='success')
        return redirect(url_for('router.commands_page'))
    commands = Handlers.query.filter_by(is_command=True).all()
    return render_template('commands.html', commands=commands)


@router.route('/events', methods=['GET', 'POST'])
def events_page():
    """
    Page to view and add events.
    """
    if request.method == 'POST':
        minutes = int(request.form.get('minutes'))
        event_action = request.form.get('event_action')
        if minutes is None or event_action is None:
            flash('Invalid from submission.', category='error')
            return redirect(url_for('router.events_page'))

        new_event = Handlers(is_command=False, is_reply=False,
                             is_event=True, trigger=None,
                             minutes=minutes, action=event_action)
        db.session.add(new_event)
        db.session.commit()
        flash("Event Created.", category='success')
        return redirect(url_for('router.events_page'))

    events = Handlers.query.filter_by(is_event=True).all()
    return render_template('events.html', events=events)


@router.route('/settings', methods=['GET', 'POST'])
def bot_settings_page():
    """
    Page to set up user-bot.
    When user sets credentials, we test by instantiating KickBot.
    If error when testing KickBot, we will flash the error message.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username is None or password is None:
            flash("Invalid form submission", category='error')
            return redirect(url_for('router.router.bot_settings_page'))
        try:
            already_bot = BotSettings.query.first()
            if already_bot:
                if already_bot.username != username or already_bot.password != password:
                    KickBot(username, password)
                    already_bot.username = username
                    already_bot.password = password
                    flash("Bot Updated.", category='success')
            else:
                KickBot(username, password)
                new_bot = BotSettings(username=username, password=password)
                db.session.add(new_bot)
                flash("Bot Added Successfully.", category='success')
            db.session.commit()
            return redirect(url_for('router.bot_settings_page'))
        except Exception as e:
            flash(f"Error verifying bot: {str(e)}", category='error')
            return redirect(url_for('router.bot_settings_page'))

    bot = BotSettings.query.first()
    return render_template('settings.html', bot=bot)


@router.route('/commands/delete/<int:command_id>')
def delete_command(command_id: int):
    """
    Route to delete commands.
    """
    command = Handlers.query.filter_by(id=command_id).first()
    if command:
        db.session.delete(command)
        db.session.commit()
        flash('Successfully Deleted Command.', category='success')
    return redirect(url_for('router.commands_page'))


@router.route('/events/delete/<int:event_id>')
def delete_event(event_id: int):
    """
    Route to delete events.
    """
    event = Handlers.query.filter_by(id=event_id).first()
    if event:
        db.session.delete(event)
        db.session.commit()
        flash('Successfully Deleted Event.', category='success')
    return redirect(url_for('router.events_page'))


@router.route('/killbot')
def kill_bot():
    """
    Route to stop the bot and clear the log.
    """
    if flask_app.bot_manager.bot_process:
        flask_app.bot_manager.bot_process.kill()
        flask_app.bot_manager.bot_running = False
        open(flask_app.bot_manager.log_filename, 'w').close()
        flash("Bot stopped.", category='success')
    return redirect(url_for('router.home_page'))
