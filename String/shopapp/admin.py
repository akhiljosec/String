from django.contrib import admin
from .models import Product

# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_seller', 'product_subject', 'product_type', 'product_name', 'product_price', 'product_details', 'product_poster', 'product_created', 'product_availability']


# admin.site.register(Product, ProductAdmin)