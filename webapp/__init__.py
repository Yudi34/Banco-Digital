import os
import secrets
from datetime import timedelta

from flask import Flask
from flask import abort, request, session

from money import format_brl
from .routes import bp


def create_app() -> Flask:
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("FLASK_ENV") == "production",
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
    )

    app.jinja_env.filters["brl"] = format_brl

    @app.context_processor
    def inject_csrf_token():
        token = session.get("csrf_token")
        if not token:
            token = secrets.token_urlsafe(32)
            session["csrf_token"] = token
        return {"csrf_token": token}

    @app.before_request
    def protect_post_requests():
        if request.method == "POST":
            sent_token = request.form.get("csrf_token", "")
            session_token = session.get("csrf_token", "")
            if not sent_token or not session_token or not secrets.compare_digest(sent_token, session_token):
                abort(400, description="Token CSRF inválido.")

    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if request.is_secure:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    app.register_blueprint(bp)
    return app
