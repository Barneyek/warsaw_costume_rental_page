from django.contrib import admin
from .models import Inquiry


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_email', 'status', 'created_at')
    list_filter = ('status',)
    readonly_fields = ('customer_name', 'customer_email', 'message', 'created_at', 'items')
    filter_horizontal = ('items',)
