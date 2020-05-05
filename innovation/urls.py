"""innovation URL configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.urls import include, path
from rest_framework import routers

from innovation.views import (
    PingView,
    OrderCreateView,
    OrderListView,
    OrderDetailView,
    OrderUpdateView,
    OrderDeleteView,
    OrderCalculateView,
    OrderResultDetailView,
)

router = routers.DefaultRouter()
#router.register('',,base_ name='')

urlpatterns = [
    path(r'admin/doc/', include('django.contrib.admindocs.urls')),
    path(r'admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('users/', include('django.contrib.auth.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path(r'ping', PingView.as_view(), name='ping'),
    path(r'api/', include(router.urls)),

    path('order/<int:pk>/edit/',
         OrderUpdateView.as_view(), name='order_edit'),
    path('order/<int:pk>/',
         OrderDetailView.as_view(), name='order_detail'),
    path('order/<int:pk>/delete/',
         OrderDeleteView.as_view(), name='order_delete'),
    path('order/new/', OrderCreateView.as_view(), name='order_new'),
    path(
        'order/<int:pk>/calculate/',
        OrderCalculateView.as_view(), name='order_calculate'
    ),
    path('order/', OrderListView.as_view(), name='order_list'),
    path(
        'order_result/<int:pk>/',
        OrderResultDetailView.as_view(), name='order_result_detail'
    ),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
