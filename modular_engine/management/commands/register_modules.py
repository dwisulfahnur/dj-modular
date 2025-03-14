import importlib
from django.conf import settings
from django.core.management.base import BaseCommand
from modular_engine.module_registry import get_registry


class Command(BaseCommand):
    help = 'Register modules listed in settings.AVAILABLE_MODULES'

    def handle(self, *args, **kwargs):
        self.stdout.write(
            'Registering modules from settings.AVAILABLE_MODULES...')

        if not hasattr(settings, 'AVAILABLE_MODULES'):
            self.stdout.write(self.style.ERROR(
                'No AVAILABLE_MODULES found in settings'))
            return

        registry = get_registry()
        registered_count = 0

        for module_id in settings.AVAILABLE_MODULES:
            self.stdout.write(f'Processing module: {module_id}')

            if module_id in registry.available_modules:
                self.stdout.write(
                    f'  Module {module_id} is already registered')
                continue

            try:
                module = importlib.import_module(f"{module_id}.module")

                if hasattr(module, 'register'):
                    module.register(registry)
                    registered_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'  Successfully registered module: {module_id}'))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'  Module {module_id} has no register function'))
            except (ImportError, AttributeError) as e:
                self.stdout.write(self.style.ERROR(
                    f'  Error loading module {module_id}: {e}'))

        self.stdout.write(
            f'Registered modules: {list(registry.available_modules.keys())}')
        self.stdout.write(self.style.SUCCESS(
            f'Successfully registered {registered_count} new modules'))
