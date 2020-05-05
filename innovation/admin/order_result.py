from django.contrib import admin

from innovation.models import OrderResult


@admin.register(OrderResult)
class OrderResultAdmin(admin.ModelAdmin):
    pass
