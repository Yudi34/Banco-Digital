import os

from webapp import create_app


app = create_app()


if __name__ == "__main__":
    debug_enabled = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_enabled)
