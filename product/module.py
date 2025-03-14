from django.urls import path
from product import views
from product.permissions import setup_product_permissions, remove_product_permissions

def setup_module():
    """Setup function to be called when the module is installed"""
    # Set up groups and permissions
    setup_product_permissions()


def cleanup_module():
    """Cleanup function to be called when the module is uninstalled"""
    # Clean up groups and permissions
    remove_product_permissions()


def register(registry):
    """Register this module with the registry"""
    from product.urls import url_patterns

    # Register the module
    registry.register_module(
        module_id='product',
        name='Product Module',
        description='A sample module for managing products with CRUD operations',
        version='1.1.0',
        app_name='product',
        url_patterns=url_patterns,
        setup_func=setup_module,
    )
