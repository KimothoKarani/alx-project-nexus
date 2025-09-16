from django.contrib import admin
from .models import Category, Product, Review

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('parent',)
    search_fields = ('name', 'description')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category', 'price', 'stock_quantity', 'is_available', 'owner', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('category', 'is_available', 'owner', 'created_at')
    search_fields = ('name', 'description', 'sku', 'brand')
    raw_id_fields = ('category', 'owner') # Will use raw ID for FKs if many objects

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review)