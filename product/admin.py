from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from product.models import Product
from product.permissions import PRODUCT_USER_GROUP, PRODUCT_MANAGER_GROUP

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'barcode', 'price', 'stock', 'created_at', 'updated_at')
    search_fields = ('name', 'barcode')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


# Custom admin action to add users to product groups
@admin.action(description="Add selected users to Product Users group")
def add_to_product_users(modeladmin, request, queryset):
    group, _ = Group.objects.get_or_create(name=PRODUCT_USER_GROUP)
    for user in queryset:
        user.groups.add(group)
    modeladmin.message_user(request, f"{queryset.count()} users added to {PRODUCT_USER_GROUP} group")


@admin.action(description="Add selected users to Product Managers group")
def add_to_product_managers(modeladmin, request, queryset):
    group, _ = Group.objects.get_or_create(name=PRODUCT_MANAGER_GROUP)
    for user in queryset:
        user.groups.add(group)
    modeladmin.message_user(request, f"{queryset.count()} users added to {PRODUCT_MANAGER_GROUP} group")


@admin.action(description="Remove selected users from Product groups")
def remove_from_product_groups(modeladmin, request, queryset):
    groups = Group.objects.filter(name__in=[PRODUCT_USER_GROUP, PRODUCT_MANAGER_GROUP])
    for user in queryset:
        user.groups.remove(*groups)
    modeladmin.message_user(request, f"{queryset.count()} users removed from Product groups")


# Unregister the default UserAdmin
admin.site.unregister(User)

# Register our custom UserAdmin with product group actions
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    actions = [add_to_product_users, add_to_product_managers, remove_from_product_groups]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_in_product_groups')
    
    def is_in_product_groups(self, obj):
        """Custom field to display which product groups the user belongs to"""
        groups = []
        if obj.groups.filter(name=PRODUCT_USER_GROUP).exists():
            groups.append("User")
        if obj.groups.filter(name=PRODUCT_MANAGER_GROUP).exists():
            groups.append("Manager")
        return ", ".join(groups) if groups else "None"
    
    is_in_product_groups.short_description = "Product Roles"
