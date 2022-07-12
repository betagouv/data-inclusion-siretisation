from django.contrib import admin
from django.urls import include, path

import annotation.views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("meta.urls")),
    path("", annotation.views.index),
    path("progress", annotation.views.progress),
    path("search", annotation.views.search),
    path("task", annotation.views.task),
    path("submit", annotation.views.submit),
]
