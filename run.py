import os
import sys
from django.core.wsgi import get_wsgi_application

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dj_modular.settings')

# Add the project directory to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Get the WSGI application
application = get_wsgi_application()

if __name__ == '__main__':
    from gunicorn.app.wsgiapp import run
    run()
