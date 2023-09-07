from . import create_app, socketio

app = create_app()


def main():
    """
    main entry point function for console script and 'python -m kickbotui'
    """
    try:
        print("App running at http://127.0.0.1:8000")
        socketio.run(app, host='127.0.0.1', port=8000)
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
