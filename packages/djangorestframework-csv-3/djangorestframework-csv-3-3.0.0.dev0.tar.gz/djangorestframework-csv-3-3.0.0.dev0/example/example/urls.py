"""example URL Configuration"""
from __future__ import annotations

from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers

from example import views

router = routers.DefaultRouter()
router.register(r"talks", views.TalkViewSet)

urlpatterns = [
    url(r"^", include(router.urls)),
    url(r"^admin/", admin.site.urls),
]
