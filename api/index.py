import os
import sys

# Ensure root directory is on the Python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from project import app

# Explicitly configure template and static folders for Vercel's serverless environment
app.template_folder = os.path.join(root_dir, 'templates')
app.static_folder = os.path.join(root_dir, 'static')

# WSGI Middleware to restore the real requested URL when Vercel rewrites to /api/index
class VercelPathMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        matched_path = (
            environ.get('HTTP_X_MATCHED_PATH')
            or environ.get('HTTP_X_VERCEL_PATH')
            or environ.get('HTTP_X_FORWARDED_PATH')
            or environ.get('HTTP_X_FORWARDED_URI')
        )
        if matched_path and matched_path != '/api/index':
            environ['PATH_INFO'] = matched_path.split('?')[0]
        elif environ.get('PATH_INFO') == '/api/index':
            environ['PATH_INFO'] = '/'

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)

# Fallback route in case /api/index is called directly
@app.route('/api/index')
def vercel_entry_fallback():
    from flask import redirect, url_for
    return redirect(url_for('dashboard'))
