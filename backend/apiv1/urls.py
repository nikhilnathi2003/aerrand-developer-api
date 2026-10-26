from django.urls import path

from . import views

urlpatterns = [
    path("health", views.health, name="health"),
    path("service-areas", views.service_areas, name="service-areas"),

    # API keys (Nikhil)
    path("keys", views.create_test_key, name="create-test-key"),
    path("keys/revoke", views.revoke_test_key, name="revoke-test-key"),
    path("keys/rotate", views.rotate_test_key, name="rotate-test-key"),
    path("keys/audit", views.audit_log, name="audit-log"),

    # pricing + booking (Sujith)
    path("quotes", views.quotes, name="quotes"),
    path("errands", views.errands_collection, name="errands"),
    path("errands/<str:errand_id>", views.get_errand, name="get-errand"),

    # wallet (Charan)
    path("wallet", views.wallet_balance, name="wallet"),
    path("wallet/topup", views.wallet_topup, name="wallet-topup"),

    # tracking + cancel (Sai)
    path("errands/<str:errand_id>/tracking", views.track_errand, name="track-errand"),
    path("errands/<str:errand_id>/cancel", views.cancel_errand, name="cancel-errand"),
    path("errands/<str:errand_id>/advance", views.advance_errand, name="advance-errand"),

    # webhooks (team)
    path("webhooks", views.webhooks_collection, name="webhooks"),
    path("events", views.events_list, name="events"),
]
