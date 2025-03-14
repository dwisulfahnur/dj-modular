from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from product.models import Product
from product.permissions import PublicAccessMixin, UserRequiredMixin, ManagerRequiredMixin


class ProductListView(PublicAccessMixin, ListView):
    """List all products - public access allowed"""
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'


class ProductDetailView(PublicAccessMixin, DetailView):
    """View a product's details - public access allowed"""
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'


class ProductCreateView(UserRequiredMixin, CreateView):
    """Create a new product - requires user role"""
    model = Product
    template_name = 'product/product_form.html'
    fields = ['name', 'barcode', 'price', 'stock']
    success_url = reverse_lazy('product_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        return context


class ProductUpdateView(UserRequiredMixin, UpdateView):
    """Update a product - requires user role"""
    model = Product
    template_name = 'product/product_form.html'
    fields = ['name', 'barcode', 'price', 'stock']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Update'
        return context
        
    def get_success_url(self):
        return reverse_lazy('product_detail', kwargs={'pk': self.object.pk})


class ProductDeleteView(ManagerRequiredMixin, DeleteView):
    """Delete a product - requires manager role"""
    model = Product
    template_name = 'product/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Product deleted successfully")
        return super().delete(request, *args, **kwargs)
        
    def get(self, request, *args, **kwargs):
        """
        GET requests will still render the confirmation page for backward compatibility
        and in case JavaScript is disabled
        """
        return super().get(request, *args, **kwargs)
