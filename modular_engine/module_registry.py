import logging
import importlib
from django.conf import settings
from django.urls import clear_url_caches, include, path, get_resolver, set_urlconf
from django.utils import timezone
from django.db import connection
from django.db import DatabaseError
from modular_engine.models import Module

logger = logging.getLogger(__name__)


class ModuleRegistry:
    """Class to handle registration and management of modules"""

    def __init__(self):
        self.modules = {}
        self.available_modules = {}

    def register_module(self, module_id, name, description, version, app_name, setup_func=None, url_patterns=None):
        """Register a module in the registry"""
        self.available_modules[module_id] = {
            'module_id': module_id,
            'name': name,
            'description': description,
            'version': version,
            'app_name': app_name,
            'setup_func': setup_func,
            'url_patterns': url_patterns,
        }

        # Just clear URL caches instead of using signals
        clear_url_caches()

    def install_module(self, module_id, base_path=None):
        """Install a module and mark it as installed in the database"""

        if module_id not in self.available_modules:
            logger.error(f"Module {module_id} not found in registry")
            return False

        module_info = self.available_modules[module_id]

        # Run setup function if provided
        if module_info.get('setup_func'):
            try:
                module_info['setup_func']()
            except Exception as e:
                logger.error(
                    f"Error running setup for module {module_id}: {e}")
                return False

        # Check if module already exists to determine dates
        module_exists = Module.objects.filter(module_id=module_id).exists()
        old_path = ""

        if module_exists:
            try:
                existing_module = Module.objects.get(module_id=module_id)
                old_path = existing_module.base_path
            except:
                pass

        defaults = {
            'name': module_info['name'],
            'description': module_info['description'],
            'version': module_info['version'],
            'status': 'installed',
        }

        # If base_path is provided, save it
        if base_path is not None:
            defaults['base_path'] = base_path

        # Set dates based on whether the module exists
        if not module_exists:
            defaults['install_date'] = timezone.now()
        else:
            defaults['update_date'] = timezone.now()

        # Update or create the module record
        module, created = Module.objects.update_or_create(
            module_id=module_id,
            defaults=defaults
        )

        # Add module to active modules
        self.modules[module_id] = module_info

        # If base_path was provided and changed, reload URLs directly
        if base_path is not None and base_path != old_path:
            logger.info(
                f"Module path changed for {module_id} from '{old_path}' to '{base_path}'")
            self._reload_urls()

        # Reload URLs
        self._reload_urls()

        return True

    def uninstall_module(self, module_id):
        """Uninstall a module and mark it as not installed in the database"""

        if module_id not in self.modules:
            logger.error(f"Module {module_id} not found in active modules")
            return False

        # Update the module record
        try:
            module = Module.objects.get(module_id=module_id)
            module.status = 'not_installed'
            module.save()
        except Module.DoesNotExist:
            logger.error(f"Module {module_id} not found in database")
            return False

        # Remove module from active modules
        self.modules.pop(module_id, None)

        # Reload URLs
        self._reload_urls()

        return True

    def check_upgrade_available(self, module_id):
        """Check if an upgrade is available for a module"""

        if module_id not in self.available_modules:
            return False

        try:
            module = Module.objects.get(module_id=module_id)
            registered_version = self.available_modules[module_id]['version']

            if module.version != registered_version:
                return True

            return False
        except Module.DoesNotExist:
            return False

    def upgrade_module(self, module_id):
        """Upgrade a module to the latest version"""

        if module_id not in self.available_modules:
            logger.error(f"Module {module_id} not found in registry")
            return False

        if module_id not in self.modules:
            logger.error(f"Module {module_id} not installed")
            return False

        module_info = self.available_modules[module_id]

        try:
            module = Module.objects.get(module_id=module_id)

            # Update the module record
            module.version = module_info['version']
            module.update_date = timezone.now()
            module.status = 'installed'
            module.save()

            # Update active modules
            self.modules[module_id] = module_info

            return True
        except Module.DoesNotExist:
            logger.error(f"Module {module_id} not found in database")
            return False

    def update_module_path(self, module_id, new_base_path):
        """Update the base path for a module"""
        if module_id not in self.available_modules:
            logger.error(f"Module {module_id} not found in registry")
            return False

        try:
            module = Module.objects.get(module_id=module_id)
            old_path = module.base_path
            module.base_path = new_base_path
            module.save()

            # Directly reload URLs instead of using signals
            self._reload_urls()

            # Log the path change
            logger.info(
                f"Updated module path for {module_id} from '{old_path}' to '{new_base_path}'")

            # Call reload_urls for backward compatibility
            self._reload_urls()

            return True
        except Module.DoesNotExist:
            logger.error(f"Module {module_id} not found in database")
            return False

    def get_active_modules(self):
        """Get list of active modules"""
        return self.modules

    def get_all_modules(self):
        """Get list of all registered modules with their status"""

        result = []

        for module_id, module_info in self.available_modules.items():
            status = 'not_installed'
            version = module_info['version']
            install_date = None
            update_date = None
            base_path = ''

            try:
                module = Module.objects.get(module_id=module_id)
                status = module.status
                install_date = module.install_date
                update_date = module.update_date
                base_path = module.base_path

                # Check if upgrade is available
                if status == 'installed' and self.check_upgrade_available(module_id):
                    status = 'upgrade_available'
                    module.status = status
                    module.save()
            except Module.DoesNotExist:
                pass

            result.append({
                'module_id': module_id,
                'name': module_info['name'],
                'description': module_info['description'],
                'version': version,
                'status': status,
                'install_date': install_date,
                'update_date': update_date,
                'base_path': base_path
            })

        return result

    def _reload_urls(self):
        """Reload URLs to include active modules"""
        # Clear URL caches directly instead of using signals
        clear_url_caches()

        # Reset the URLconf for the current thread
        set_urlconf(None)

        # Reload main URLconf module if needed
        if hasattr(settings, 'ROOT_URLCONF'):
            import sys
            import importlib
            urlconf = settings.ROOT_URLCONF
            if urlconf in sys.modules:
                importlib.reload(sys.modules[urlconf])


# Singleton instance of the registry
registry = ModuleRegistry()


def initialize_module_registry():
    # Avoid database access during app initialization
    if not connection.is_usable():
        return

    # Check if the table exists before trying to query it
    try:
        # Load modules from the database
        installed_modules = Module.objects.filter(status='installed')

        # Register available modules from settings
        if hasattr(settings, 'AVAILABLE_MODULES'):
            print(
                f"Found AVAILABLE_MODULES in settings: {settings.AVAILABLE_MODULES}")
            for module_id in settings.AVAILABLE_MODULES:
                try:
                    # Try to import the module
                    print(f"Attempting to import module: {module_id}")
                    module = importlib.import_module(f"{module_id}.module")

                    # Register the module
                    if hasattr(module, 'register'):
                        print(f"Registering module: {module_id}")
                        module.register(registry)
                        print(f"Module {module_id} registered successfully")
                    else:
                        print(f"Module {module_id} has no register function")
                except (ImportError, AttributeError) as e:
                    print(f"Error loading module {module_id}: {e}")
                    logger.error(f"Error loading module {module_id}: {e}")
        else:
            print("No AVAILABLE_MODULES found in settings")

        # Activate installed modules
        for module in installed_modules:
            if module.module_id in registry.available_modules:
                registry.modules[module.module_id] = registry.available_modules[module.module_id]

                # Check for available upgrades
                if registry.check_upgrade_available(module.module_id):
                    module.status = 'upgrade_available'
                    module.save()
            else:
                # Module was installed but is no longer available
                module.status = 'not_installed'
                module.save()

        print(f"Registered modules: {registry.available_modules.keys()}")
        print(f"Active modules: {registry.modules.keys()}")
    except DatabaseError:
        # Table doesn't exist yet, migrations haven't been run
        print("Database error during module registry initialization")
        pass

    return registry


# Helper function to get the registry
def get_registry():
    return registry


# Dynamic module URL patterns
def get_module_url_patterns():
    """
    Get URL patterns for all available modules.
    The patterns include all registered modules that have url_patterns defined.
    The base path for each module is determined from the Module model.
    """
    module_patterns = []
    registry = get_registry()

    # Include URL patterns for all available modules
    for module_id, module_info in registry.available_modules.items():
        if not module_info.get('url_patterns'):
            continue

        try:
            # Try to get the module from the database to check for custom base path and status 'installed'
            module = Module.objects.get(module_id=module_id, status='installed')

            # Get the base path (custom or default)
            base_path = module.get_url_path()

            # Create the URL pattern with the appropriate base path
            if base_path == '/':
                # Root path
                module_patterns.append(
                    path('', include(module_info['url_patterns']))
                )
            else:
                # Regular path
                module_patterns.append(
                    path(f"{base_path}/", include(module_info['url_patterns']))
                )
        except Module.DoesNotExist:
            # Module not in database, dont add the module to the url patterns
            pass

    return module_patterns


# Function to manually register modules from settings
def register_modules_from_settings():
    """
    Manually register all modules listed in settings.AVAILABLE_MODULES.
    This can be used if automatic registration during app initialization fails.
    """
    if not hasattr(settings, 'AVAILABLE_MODULES'):
        logger.warning("No AVAILABLE_MODULES found in settings")
        return 0

    count = 0
    for module_id in settings.AVAILABLE_MODULES:
        if module_id in registry.available_modules:
            logger.info(f"Module {module_id} is already registered")
            continue

        try:
            module = importlib.import_module(f"{module_id}.module")

            if hasattr(module, 'register'):
                module.register(registry)
                count += 1
                logger.info(f"Successfully registered module: {module_id}")
            else:
                logger.warning(f"Module {module_id} has no register function")
        except (ImportError, AttributeError) as e:
            logger.error(f"Error loading module {module_id}: {e}")

    return count
