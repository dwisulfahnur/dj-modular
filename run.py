import os
import sys
import importlib
from django.core.wsgi import get_wsgi_application
from django.urls import clear_url_caches, set_urlconf

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djmodular.settings')

# Add the project directory to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize the application and ensure URL patterns are loaded


def initialize_application():
    # Ensure all modules from settings are registered
    from modular_engine.module_registry import register_modules_from_settings
    register_modules_from_settings()

    # Clear URL caches and reload URLs to ensure proper module URL patterns
    clear_url_caches()
    set_urlconf(None)

    # Reload main URLconf module
    if 'djmodular.urls' in sys.modules:
        importlib.reload(sys.modules['djmodular.urls'])

    # Get the WSGI application
    return get_wsgi_application()


# Initialize once at module level (shared among all workers)
application = initialize_application()

if __name__ == '__main__':
    from gunicorn.app.wsgiapp import run
    run()
