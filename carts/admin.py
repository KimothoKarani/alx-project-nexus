from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline): # Display CartItems directly in Cart admin
    model = CartItem
    extra = 0 # Don't show extra empty forms by default
    raw_id_fields = ('product',) # Use raw ID for products

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email',)
    inlines = [CartItemInline] # Embed CartItems

admin.site.register(Cart, CartAdmin)
# admin.site.register(CartItem) # Usually managed via CartAdmin, but can be registered separately