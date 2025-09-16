from django.contrib import admin
from .models import Order, OrderItem, Payment

class OrderItemInline(admin.TabularInline): # Display OrderItems directly in Order admin
    model = OrderItem
    extra = 0
    raw_id_fields = ('product',)

class PaymentInline(admin.StackedInline): # Display Payment directly in Order admin
    model = Payment
    extra = 0
    max_num = 1 # Only one payment per order

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_amount', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at', 'updated_at')
    search_fields = ('user__email', 'id')
    inlines = [OrderItemInline, PaymentInline]
    raw_id_fields = ('user', 'shipping_address', 'billing_address') # Use raw ID for FKs

admin.site.register(Order, OrderAdmin)
# admin.site.register(OrderItem) # Usually managed via OrderAdmin
# admin.site.register(Payment) # Usually managed via OrderAdmin