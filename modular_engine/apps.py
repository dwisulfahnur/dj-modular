from django.apps import AppConfig


class ModularEngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modular_engine'
    verbose_name = 'Modular Engine'

    def ready(self):
        """Initialize the module registry when the app is ready"""
        # Skip initialization during migrations
        import sys
        if 'makemigrations' in sys.argv or 'migrate' in sys.argv:
            return

        # Import here to avoid circular imports
        import importlib
        from django.conf import settings
        from modular_engine.module_registry import initialize_module_registry, get_registry

        # Initialize the module registry
        initialize_module_registry()

        # Ensure modules are loaded from settings.AVAILABLE_MODULES
        registry = get_registry()
        if hasattr(settings, 'AVAILABLE_MODULES'):
            for module_id in settings.AVAILABLE_MODULES:
                if module_id not in registry.available_modules:
                    try:
                        module = importlib.import_module(f"{module_id}.module")
                        if hasattr(module, 'register'):
                            module.register(registry)
                            print(
                                f"Module {module_id} registered from AppConfig.ready()")
                    except (ImportError, AttributeError) as e:
                        print(
                            f"Error loading module {module_id} from AppConfig.ready(): {e}")
