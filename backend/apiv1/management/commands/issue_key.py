"""Issue an API key for a business (keys are issued by command, not a dashboard).

Example:
    python manage.py issue_key --business "Acme Co" --env test
"""
import uuid
from datetime import datetime, timedelta, timezone

from django.core.management.base import BaseCommand, CommandError

from apiv1 import db, keys

# stable namespace so re-issuing for the same business name keeps the same owner id
_NS = uuid.UUID("a1b2c3d4-0000-4000-8000-000000000000")


class Command(BaseCommand):
    help = "Issue an API key for a business. The full key is shown once."

    def add_arguments(self, parser):
        parser.add_argument("--business", required=True, help="business name (its tenant)")
        parser.add_argument("--env", default="test", choices=["test", "live"])
        parser.add_argument("--name", default="default", help="label for the key")
        parser.add_argument("--scopes", default="create,read,cancel",
                            help="comma-separated: create,read,cancel")
        parser.add_argument("--expires-days", type=int, default=None)

    def handle(self, *args, **opts):
        scopes = [s.strip() for s in opts["scopes"].split(",") if s.strip()]
        bad = set(scopes) - keys.VALID_SCOPES
        if bad:
            raise CommandError(f"Invalid scopes: {', '.join(bad)}")

        owner_id = str(uuid.uuid5(_NS, opts["business"].strip().lower()))
        plaintext = keys.generate_key(opts["env"])

        expires_at = None
        if opts["expires_days"]:
            expires_at = datetime.now(timezone.utc) + timedelta(days=opts["expires_days"])

        db.api_keys().insert_one({
            "id": str(uuid.uuid4()),
            "business_owner_id": owner_id,
            "business_name": opts["business"],
            "name": opts["name"],
            "environment": opts["env"],
            "key_prefix": keys.prefix_of(plaintext),
            "key_hash": keys.hash_key(plaintext),
            "scopes": scopes,
            "status": "active",
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc),
            "last_used_at": None,
        })

        self.stdout.write(self.style.SUCCESS("API key created. Copy it now — it won't be shown again:\n"))
        self.stdout.write(f"  {plaintext}\n")
        self.stdout.write(f"  business : {opts['business']}  (owner {owner_id})")
        self.stdout.write(f"  env      : {opts['env']}")
        self.stdout.write(f"  scopes   : {', '.join(scopes)}")
        self.stdout.write(f"  expires  : {expires_at.isoformat() if expires_at else 'never'}")
