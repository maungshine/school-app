from flask import render_template
from . import errors

@errors.app_errorhandler(404)
def page_not_found(error):
    """return 404 not found error template when 404 error is rasied"""
    return render_template('errors/404.html'), 404

@errors.app_errorhandler(500)
def internal_server_error(error):
    """return 500 internal server error template when 500 error is rasied"""
    return render_template('errors/500.html'), 500

@errors.app_errorhandler(403)
def forbidden(error):
    """return 403 permission denied error template when 403 error is rasied"""
    return render_template('errors/403.html'), 403
