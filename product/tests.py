from django.test import TestCase, SimpleTestCase, Client, RequestFactory
from django.urls import reverse, include, path
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from decimal import Decimal

from product.models import Product
from product.permissions import PublicAccessMixin, UserRequiredMixin, ManagerRequiredMixin
from product.permissions import PRODUCT_USER_GROUP, PRODUCT_MANAGER_GROUP, setup_product_permissions
from product.views import ProductListView, ProductDetailView, ProductCreateView, ProductUpdateView, ProductDeleteView


class ProductModelTest(TestCase):
    """Tests for the Product model"""

    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            barcode="123456789",
            price=Decimal("19.99"),
            stock=10
        )

    def test_product_creation(self):
        """Test that a product can be created"""
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.barcode, "123456789")
        self.assertEqual(self.product.price, Decimal("19.99"))
        self.assertEqual(self.product.stock, 10)

    def test_product_str(self):
        """Test the string representation of a product"""
        self.assertEqual(str(self.product), "Test Product")


class ProductPermissionsTest(TestCase):
    """Tests for the product permissions system"""

    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(
            username="user",
            email="user@example.com",
            password="userpassword"
        )

        self.manager = User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="managerpassword",
            is_staff=True
        )

        # Create a test product
        self.product = Product.objects.create(
            name="Test Product",
            barcode="123456789",
            price=Decimal("19.99"),
            stock=10
        )

        # Set up groups and permissions
        setup_product_permissions()

        # Add users to groups
        user_group = Group.objects.get(name=PRODUCT_USER_GROUP)
        manager_group = Group.objects.get(name=PRODUCT_MANAGER_GROUP)

        self.user.groups.add(user_group)
        self.manager.groups.add(manager_group)

    def test_public_access_mixin(self):
        """Test the PublicAccessMixin"""
        # Create a mock request
        class MockRequest:
            def __init__(self, user=None):
                self.user = user

        # Create a proper mixin instance
        class TestMixin(PublicAccessMixin):
            def __init__(self, request):
                self.request = request

        # Test with anonymous user
        anonymous_request = MockRequest()
        anonymous_request.user = AnonymousUser()
        mixin = TestMixin(anonymous_request)
        self.assertTrue(mixin.test_func())

        # Test with authenticated user
        user_request = MockRequest(self.user)
        mixin = TestMixin(user_request)
        self.assertTrue(mixin.test_func())

        # Test with manager
        manager_request = MockRequest(self.manager)
        mixin = TestMixin(manager_request)
        self.assertTrue(mixin.test_func())

    def test_user_required_mixin(self):
        """Test the UserRequiredMixin"""
        # Check that user has the proper permissions
        self.assertTrue(self.user.has_perm('product.view_product'))
        self.assertTrue(self.user.has_perm('product.add_product'))
        self.assertTrue(self.user.has_perm('product.change_product'))

        # Check that manager has all permissions
        self.assertTrue(self.manager.has_perm('product.view_product'))
        self.assertTrue(self.manager.has_perm('product.add_product'))
        self.assertTrue(self.manager.has_perm('product.change_product'))
        self.assertTrue(self.manager.has_perm('product.delete_product'))

    def test_manager_required_mixin(self):
        """Test the ManagerRequiredMixin"""
        # Check that user doesn't have manager permissions
        self.assertFalse(self.user.has_perm('product.delete_product'))

        # Check that manager has all permissions including delete
        self.assertTrue(self.manager.has_perm('product.delete_product'))


class ProductViewsSimpleTest(TestCase):
    """Test product views directly without template rendering"""

    def setUp(self):
        # Create test factory
        self.factory = RequestFactory()

        # Create test users
        self.anonymous_user = AnonymousUser()

        self.user = User.objects.create_user(
            username="testuser",
            email="user@example.com",
            password="userpassword"
        )

        self.manager = User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="managerpassword",
            is_staff=True
        )

        # Create a test product
        self.product = Product.objects.create(
            name="Test Product",
            barcode="TEST001",
            price=Decimal("19.99"),
            stock=10
        )

        # Set up permissions and groups
        setup_product_permissions()

        # Add users to groups
        user_group = Group.objects.get(name=PRODUCT_USER_GROUP)
        manager_group = Group.objects.get(name=PRODUCT_MANAGER_GROUP)

        self.user.groups.add(user_group)
        self.manager.groups.add(manager_group)

    def test_product_list_view(self):
        """Test the product list view directly"""
        request = self.factory.get('/products/')
        request.user = self.anonymous_user

        response = ProductListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

        # Check with authenticated user
        request.user = self.user
        response = ProductListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_product_detail_view(self):
        """Test the product detail view directly"""
        request = self.factory.get('/products/')
        request.user = self.anonymous_user

        response = ProductDetailView.as_view()(request, pk=self.product.pk)
        self.assertEqual(response.status_code, 200)

        # Check with authenticated user
        request.user = self.user
        response = ProductDetailView.as_view()(request, pk=self.product.pk)
        self.assertEqual(response.status_code, 200)

    def test_product_create_view_permissions(self):
        """Test permissions for the product create view"""
        # Anonymous users should be redirected to login
        request = self.factory.get('/products/')
        request.user = self.anonymous_user

        response = ProductCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Authenticated users with proper permissions should have access
        request.user = self.user
        response = ProductCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)

        # Managers should have access
        request.user = self.manager
        response = ProductCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_product_update_view_permissions(self):
        """Test permissions for the product update view"""
        # Anonymous users should be redirected to login
        request = self.factory.get('/products/')
        request.user = self.anonymous_user

        response = ProductUpdateView.as_view()(request, pk=self.product.pk)
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Authenticated users with proper permissions should have access
        request.user = self.user
        response = ProductUpdateView.as_view()(request, pk=self.product.pk)
        self.assertEqual(response.status_code, 200)

        # Managers should have access
        request.user = self.manager
        response = ProductUpdateView.as_view()(request, pk=self.product.pk)
        self.assertEqual(response.status_code, 200)

    def test_product_delete_view_permissions(self):
        """Test permissions for the product delete view"""
        # Anonymous users should be redirected to login
        request = self.factory.get('/products/')
        request.user = self.anonymous_user

        response = ProductDeleteView.as_view()(request, pk=self.product.pk)
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Regular users should be denied access (raises PermissionDenied)
        request.user = self.user
        try:
            response = ProductDeleteView.as_view()(request, pk=self.product.pk)
            self.fail("PermissionDenied exception not raised")
        except PermissionDenied:
            # This is the expected behavior
            pass

        # Managers should have access
        request.user = self.manager
        response = ProductDeleteView.as_view()(request, pk=self.product.pk)
        self.assertEqual(response.status_code, 200)

    def test_product_crud_operations(self):
        """Test create, read, update, and delete operations for products"""
        # Create
        product_data = {
            'name': 'Buku Matematika',
            'barcode': '111222333',
            'price': '50000',
            'stock': '15'
        }

        request = self.factory.post('/products/', data=product_data)
        request.user = self.user

        # Add session and messages middleware attributes
        setattr(request, 'session', {})
        setattr(request, '_messages', [])

        response = ProductCreateView.as_view()(request)
        # Redirect after successful creation
        self.assertEqual(response.status_code, 302)

        # Check that the product was created
        self.assertTrue(Product.objects.filter(barcode='111222333').exists())

        # Update
        product = Product.objects.get(barcode='111222333')
        updated_data = {
            'name': 'Buku Bahasa Indonesia',
            'barcode': '111222333',
            'price': '40000',
            'stock': '50'
        }

        request = self.factory.post('/products/', data=updated_data)
        request.user = self.user

        # Add session and messages middleware attributes
        setattr(request, 'session', {})
        setattr(request, '_messages', [])

        response = ProductUpdateView.as_view()(request, pk=product.pk)
        # Redirect after successful update
        self.assertEqual(response.status_code, 302)

        # Check that the product was updated
        product.refresh_from_db()
        self.assertEqual(product.name, 'Buku Bahasa Indonesia')
        self.assertEqual(product.price, Decimal('40000'))
        self.assertEqual(product.stock, 50)

        # Delete
        request = self.factory.post('/products/')
        request.user = self.manager

        # Add session and messages middleware attributes
        setattr(request, 'session', {})
        setattr(request, '_messages', [])

        response = ProductDeleteView.as_view()(request, pk=product.pk)
        # Redirect after successful deletion
        self.assertEqual(response.status_code, 302)

        # Check that the product was deleted
        self.assertFalse(Product.objects.filter(pk=product.pk).exists())
