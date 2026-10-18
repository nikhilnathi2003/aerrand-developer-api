from django.contrib import admin
from django.urls import include, path

from apiv1 import views as apiv1_views

urlpatterns = [
    path("", apiv1_views.dashboard, name="dashboard"),
    path("admin/", admin.site.urls),
    path("v1/", include("apiv1.urls")),
]
