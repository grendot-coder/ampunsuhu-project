import os
import sys
from flask import send_from_directory

# Ensure root directory is on the Python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from project import app

# Determine static and template directories
api_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(api_dir, 'static') if os.path.exists(os.path.join(api_dir, 'static')) else os.path.join(root_dir, 'static')
template_dir = os.path.join(root_dir, 'templates')

app.static_folder = static_dir
app.template_folder = template_dir

# WSGI Middleware to fix URL prefixing & routing on Vercel
class VercelPrefixMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # Reset SCRIPT_NAME so url_for generates clean URLs without /api/index prefix
        environ['SCRIPT_NAME'] = ''

        # Strip /api/index or /api prefix from PATH_INFO if Vercel appended it
        path = environ.get('PATH_INFO', '')
        if path.startswith('/api/index'):
            path = path[len('/api/index'):] or '/'
            environ['PATH_INFO'] = path
        elif path.startswith('/api'):
            path = path[len('/api'):] or '/'
            environ['PATH_INFO'] = path

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPrefixMiddleware(app.wsgi_app)

# Explicit route to ensure static files (CSS/JS) are always served on Vercel
@app.route('/static/<path:filename>')
def serve_static_assets(filename):
    return send_from_directory(static_dir, filename)
