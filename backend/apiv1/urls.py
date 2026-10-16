from django.urls import path

from . import views

urlpatterns = [
    path("health", views.health, name="health"),
    path("service-areas", views.service_areas, name="service-areas"),
    path("quotes", views.quotes, name="quotes"),
    path("errands", views.create_errand, name="create-errand"),
    path("errands/<str:errand_id>", views.get_errand, name="get-errand"),
]
