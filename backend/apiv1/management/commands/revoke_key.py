"""Revoke an API key immediately by its prefix.

Example:
    python manage.py revoke_key --prefix ak_test_A1B2C3
"""
from datetime import datetime, timezone

from django.core.management.base import BaseCommand, CommandError

from apiv1 import db


class Command(BaseCommand):
    help = "Revoke an API key by its prefix. Revocation is immediate and irreversible."

    def add_arguments(self, parser):
        parser.add_argument("--prefix", required=True, help="the key_prefix, e.g. ak_test_A1B2C3")

    def handle(self, *args, **opts):
        result = db.api_keys().update_one(
            {"key_prefix": opts["prefix"], "status": {"$ne": "revoked"}},
            {"$set": {"status": "revoked", "revoked_at": datetime.now(timezone.utc)}},
        )
        if result.matched_count == 0:
            raise CommandError(f"No active key found with prefix {opts['prefix']}")
        self.stdout.write(self.style.SUCCESS(f"Revoked key {opts['prefix']}."))
