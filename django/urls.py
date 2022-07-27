from django.contrib import admin
from django.urls import include, path

import annotation.views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("meta.urls")),
    path("", annotation.views.index),
    path("partials/progress", annotation.views.partial_progress),
    path("partials/search", annotation.views.partial_search),
    path("partials/task", annotation.views.partial_task),
    path("partials/submit", annotation.views.partial_submit),
]
