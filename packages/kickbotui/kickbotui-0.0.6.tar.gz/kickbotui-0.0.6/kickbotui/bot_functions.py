import subprocess
import random
import sys

from collections import namedtuple

from . import socketio, flask_app
from .models import Handlers

CommandFunction = namedtuple('CommandFunction', ['trigger', 'func_name', 'func_string'])
EventFunction = namedtuple('EventFunction', ['minutes', 'func_name', 'func_string'])


def escape_quotes(to_send):
    to_send = to_send.replace("'", "\\'")
    to_send = to_send.replace('"', '\\"')
    return to_send


def generate_function_name(trigger):
    """
    Generate a unique function name based on the trigger.
    """
    if trigger:
        func_name = "".join([char for char in trigger if char.isalpha()])
    else:
        func_name = "event"
    return f"{func_name}{random.randint(100000, 999999)}"


def generate_command_function_string(handler):
    """
    Generate the function string for a command handler.
    """
    func_name = generate_function_name(handler.trigger)
    func_string = f"async def {func_name}(bot: KickBot, message: KickMessage):\n"
    to_send = escape_quotes(handler.action)
    if handler.is_reply:
        func_string += f"    await bot.reply_text(message, '{to_send}')\n\n\n"
    else:
        func_string += f"    await bot.sent_text('{to_send}')\n\n\n"
    return CommandFunction(escape_quotes(handler.trigger), func_name, func_string)


def generate_event_function_string(handler):
    """
    Generate the function string for a timed event.
    """
    func_name = generate_function_name(handler.trigger)
    func_string = f"async def {func_name}(bot: KickBot):\n"
    to_send = escape_quotes(handler.action)
    func_string += f"    await bot.send_text('{to_send}')\n\n\n"
    return EventFunction(handler.minutes, func_name, func_string)


def create_command_file(handlers, temp_file_path):
    """
    Create a temporary Python file for the bot.
    """
    command_funcs = []
    event_funcs = []
    for handler in handlers:
        if handler.is_command:
            command_funcs.append(generate_command_function_string(handler))
        elif handler.is_event:
            event_funcs.append(generate_event_function_string(handler))
    with open(temp_file_path, 'w') as f:
        f.write("import sys\nfrom datetime import timedelta\nfrom kickbot import KickBot, KickMessage\n\n\n")
        for func in command_funcs:
            f.write(func.func_string)
        for func in event_funcs:
            f.write(func.func_string)
        f.write("if __name__ == '__main__':\n"
                "    bot = KickBot(sys.argv[2], sys.argv[3])\n"
                "    bot.set_streamer(sys.argv[1])\n")
        for func in command_funcs:
            f.write(f"    bot.add_command_handler('{func.trigger}', {func.func_name})\n")
        for func in event_funcs:
            f.write(f"    bot.add_timed_event(timedelta(minutes={func.minutes}), {func.func_name})\n")
        f.write('    bot.poll()\n')


def run_bot(streamer, username, password):
    """
    Generate a file based on the handlers/events and
    Create a subprocess to run generated file.
    streamer, username, and password are passed to generated file by sys argv.
    Write stdout of subprocess to log file to be sent to dashboard over socket.
    """
    python_exe = sys.executable
    with flask_app.app_context():
        handlers = Handlers.query.filter_by().all()
    create_command_file(handlers, flask_app.bot_manager.temp_file)
    flask_app.bot_manager.bot_running = True
    with open(flask_app.bot_manager.log_filename, "w") as log_file:
        flask_app.bot_manager.bot_process = subprocess.Popen(
            [python_exe, flask_app.bot_manager.temp_file, streamer, username, password],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True
        )


def send_bot_output():
    """
    Send new output logs to the dashboard and add them to sent lines.
    If user refreshes dashboard page, sent lines are cleared, so all logs are sent back, making it appear same as before.
    """
    while True:
        if flask_app.bot_manager.bot_running:
            try:
                with open(flask_app.bot_manager.log_filename, "r", encoding='utf-8') as log_file:
                    lines = log_file.readlines()
                for line in lines:
                    if line not in flask_app.bot_manager.sent_lines:
                        socketio.emit('bot_output', line.strip())
                        flask_app.bot_manager.sent_lines.append(line)
            except Exception as e:
                print("Error sending bot output:", str(e))
        socketio.sleep(1)
