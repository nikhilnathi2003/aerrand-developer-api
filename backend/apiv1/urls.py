from django.urls import path

from . import views

urlpatterns = [
    path("health", views.health, name="health"),
    path("service-areas", views.service_areas, name="service-areas"),
    path("keys", views.create_test_key, name="create-test-key"),
    path("keys/revoke", views.revoke_test_key, name="revoke-test-key"),
    path("quotes", views.quotes, name="quotes"),
    path("errands", views.errands_collection, name="errands"),
    path("errands/<str:errand_id>", views.get_errand, name="get-errand"),
]
