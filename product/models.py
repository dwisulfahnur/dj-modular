from django.db import models
from django.core.validators import MinValueValidator


class Product(models.Model):
    """Product model with name, barcode, price and stock"""
    name = models.CharField(max_length=200)
    barcode = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            ("can_view_inventory", "Can view inventory levels"),
            ("can_update_price", "Can update product prices"),
            ("can_manage_stock", "Can manage stock levels"),
        ]

    def __str__(self):
        return self.name

    @staticmethod
    def user_has_product_permissions(user):
        """
        Helper method to check if a user has any product-related permissions
        via either explicit permissions or group membership.

        Returns: bool - True if user has permissions, False otherwise
        """
        if not user.is_authenticated:
            return False

        # Check if user is a superuser or staff (always has permissions)
        if user.is_superuser or user.is_staff:
            return True

        # Check group membership for product roles
        from product.permissions import PRODUCT_USER_GROUP, PRODUCT_MANAGER_GROUP
        if user.groups.filter(name__in=[PRODUCT_USER_GROUP, PRODUCT_MANAGER_GROUP]).exists():
            return True

        # Check if user has any explicit product permissions
        product_perms = ['view_product', 'add_product', 'change_product', 'delete_product',
                         'can_view_inventory', 'can_update_price', 'can_manage_stock']

        for perm in product_perms:
            if user.has_perm(f'product.{perm}'):
                return True

        return False
