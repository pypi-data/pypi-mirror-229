import subprocess

from . import create_app

app = create_app()


def main():
    """
    main entry point function for console script and 'python -m kickbotui'
    """
    try:
        subprocess.call(["gunicorn", "-k",
                         "geventwebsocket.gunicorn.workers.GeventWebSocketWorker",
                         "kickbotui.app:app"])
    except KeyboardInterrupt:
        pass
    finally:
        if app.bot_manager.bot_process:
            open(app.bot_manager.log_filename, 'w').close()
            app.bot_manager.bot_process.kill()
            app.bot_manager.bot_running = False
        raise SystemExit()


if __name__ == '__main__':
    main()
