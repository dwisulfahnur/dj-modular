from django.contrib.auth.mixins import UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from product.models import Product

# Define group names as constants for consistency
PRODUCT_USER_GROUP = 'Product Users'
PRODUCT_MANAGER_GROUP = 'Product Managers'


def setup_product_permissions():
    """
    Create the necessary groups and permissions for the product module.
    This should be called when the module is installed.
    """
    # Get the content type for the Product model
    product_content_type = ContentType.objects.get_for_model(Product)

    # Get or create the basic permissions for the Product model
    view_permission, _ = Permission.objects.get_or_create(
        codename='view_product',
        content_type=product_content_type,
        defaults={'name': 'Can view product'}
    )
    add_permission, _ = Permission.objects.get_or_create(
        codename='add_product',
        content_type=product_content_type,
        defaults={'name': 'Can add product'}
    )
    change_permission, _ = Permission.objects.get_or_create(
        codename='change_product',
        content_type=product_content_type,
        defaults={'name': 'Can change product'}
    )
    delete_permission, _ = Permission.objects.get_or_create(
        codename='delete_product',
        content_type=product_content_type,
        defaults={'name': 'Can delete product'}
    )

    # Get or create the custom permissions
    view_inventory_permission, _ = Permission.objects.get_or_create(
        codename='can_view_inventory',
        content_type=product_content_type,
        defaults={'name': 'Can view inventory levels'}
    )
    update_price_permission, _ = Permission.objects.get_or_create(
        codename='can_update_price',
        content_type=product_content_type,
        defaults={'name': 'Can update product prices'}
    )
    manage_stock_permission, _ = Permission.objects.get_or_create(
        codename='can_manage_stock',
        content_type=product_content_type,
        defaults={'name': 'Can manage stock levels'}
    )

    # Create the Product Users group (can view, add, and change products)
    product_users, _ = Group.objects.get_or_create(name=PRODUCT_USER_GROUP)
    product_users.permissions.add(
        view_permission,
        add_permission,
        change_permission,
        view_inventory_permission
    )

    # Create the Product Managers group (can do everything including delete)
    product_managers, _ = Group.objects.get_or_create(
        name=PRODUCT_MANAGER_GROUP)
    product_managers.permissions.add(
        view_permission,
        add_permission,
        change_permission,
        delete_permission,
        view_inventory_permission,
        update_price_permission,
        manage_stock_permission
    )


def remove_product_permissions():
    """
    Remove the groups and permissions when the module is uninstalled.
    """
    # Delete the groups (this will automatically remove the group-permission relationships)
    Group.objects.filter(
        name__in=[PRODUCT_MANAGER_GROUP]).delete()


class PublicAccessMixin(UserPassesTestMixin):
    """
    Mixin to allow public access to a view.
    This maintains backward compatibility with the old system.
    """

    def test_func(self):
        return True


class UserRequiredMixin(PermissionRequiredMixin):
    """
    Mixin to require the user to have basic product permissions.
    User must be in the Product Users group or have the specific permission.
    """
    permission_required = ('product.view_product',
                          'product.add_product',
                          'product.change_product')

    # Allow if user has ANY of the permissions (not all required)
    def has_permission(self):
        user = self.request.user
        # Check if the user is in the Product Users or Managers group
        if user.groups.filter(name__in=[PRODUCT_USER_GROUP]).exists():
            return True

        # Fall back to the standard permission check
        return super().has_permission()


class ManagerRequiredMixin(PermissionRequiredMixin):
    """
    Mixin to require the user to have manager-level product permissions.
    User must be in the Product Managers group or have delete permission.
    """
    permission_required = ('product.delete_product',)

    def has_permission(self):
        user = self.request.user
        # Check if the user is in the Product Managers group
        if user.groups.filter(name=PRODUCT_MANAGER_GROUP).exists():
            return True

        # Fall back to the standard permission check
        return super().has_permission()
