from flask import render_template
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(e):
        return render_template("error.html", message="Bad request – user input error"), 400

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", message="Page not found"), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("error.html", message="Server error"), 500

    @app.errorhandler(502)
    def api_error(e):
        return render_template("error.html", message="API error – service unavailable"), 502

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return render_template("error.html", message=e.description), e.code