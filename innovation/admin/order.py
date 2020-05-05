from django.contrib import admin

from innovation.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass
