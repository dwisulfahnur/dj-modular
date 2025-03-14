from django.urls import path
from product import views

# The product module doesn't use namespaces for tests to work correctly
url_patterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('create/', views.ProductCreateView.as_view(), name='product_create'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('<int:pk>/update/', views.ProductUpdateView.as_view(),
            name='product_update'),
    path('<int:pk>/delete/', views.ProductDeleteView.as_view(),
            name='product_delete'),
]