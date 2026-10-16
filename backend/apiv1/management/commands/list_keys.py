"""List API keys (prefix only — the full key is never stored).

Example:
    python manage.py list_keys
"""
from django.core.management.base import BaseCommand

from apiv1 import db


class Command(BaseCommand):
    help = "List API keys (prefix, business, env, scopes, status)."

    def add_arguments(self, parser):
        parser.add_argument("--business", default=None)

    def handle(self, *args, **opts):
        query = {}
        if opts["business"]:
            query["business_name"] = opts["business"]
        rows = list(db.api_keys().find(query).sort("created_at", -1))
        if not rows:
            self.stdout.write("No keys found.")
            return
        for r in rows:
            self.stdout.write(
                f"{r['key_prefix']:<16} {r['environment']:<5} "
                f"{r['status']:<8} [{','.join(r.get('scopes', []))}]  {r.get('business_name','')}"
            )
