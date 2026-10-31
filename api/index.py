import os
import sys

# Ensure root directory is on the Python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from project import app

# Explicitly configure template and static folders for Vercel
app.template_folder = os.path.join(root_dir, 'templates')
app.static_folder = os.path.join(root_dir, 'static')

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
