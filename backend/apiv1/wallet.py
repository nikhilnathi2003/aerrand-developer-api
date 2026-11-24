"""Prepaid wallet for a business — balance + full transaction history.

Balances live in the 'wallets' collection; every movement (top-up, charge, refund) is
recorded in 'wallet_transactions' so there's a complete, auditable statement.
Amounts are stored in cents to avoid floating-point errors.
"""
import hashlib
import hmac
import urllib.parse
from datetime import datetime, timezone

from . import db

# Below this balance the wallet is "low".
LOW_BALANCE_CENTS = 2000  # $20.00
# When a charge drops the wallet below the low line we email the business; new
# deliveries stay blocked until they top up manually (no auto-reload).
# Where low-balance alerts go if a business hasn't set its own address.
DEFAULT_ALERT_EMAIL = "nathinikhil28@gmail.com"
# The low-balance email offers a one-click top-up of this amount.
TOPUP_OFFER_CENTS = 5000  # $50.00
# Base URL used to build the Yes/No top-up links in the email (local demo).
PORTAL_BASE = "http://127.0.0.1:8000"
# Secret that signs the one-click top-up links so they can't be forged or tampered.
TOPUP_LINK_SECRET = "topup_link_demo_secret"


def _wallets():
    return db.get_db()["wallets"]


def _txns():
    return db.get_db()["wallet_transactions"]


def _record(owner, kind, amount_cents, errand_id=None, note=""):
    _txns().insert_one({
        "business_owner_id": owner,
        "kind": kind,                      # topup / charge / refund
        "amount_cents": int(amount_cents),  # +credit / -debit
        "errand_id": errand_id,
        "note": note,
        "at": datetime.now(timezone.utc),
    })


def get_balance(owner_id):
    w = _wallets().find_one({"business_owner_id": owner_id})
    return w["balance_cents"] if w else 0


def topup(owner_id, amount_cents, note="Top-up"):
    amount_cents = int(amount_cents)
    _wallets().update_one({"business_owner_id": owner_id},
                          {"$inc": {"balance_cents": amount_cents}}, upsert=True)
    _record(owner_id, "topup", amount_cents, note=note)
    return get_balance(owner_id)


def debit(owner_id, amount_cents, errand_id=None):
    """Atomically charge the wallet. Returns True if paid, False if funds are short."""
    amount_cents = int(amount_cents)
    result = _wallets().update_one(
        {"business_owner_id": owner_id, "balance_cents": {"$gte": amount_cents}},
        {"$inc": {"balance_cents": -amount_cents}},
    )
    if result.modified_count == 1:
        _record(owner_id, "charge", -amount_cents, errand_id, "Delivery charge")
        return True
    return False


def refund(owner_id, amount_cents, errand_id=None):
    amount_cents = int(amount_cents)
    _wallets().update_one({"business_owner_id": owner_id},
                          {"$inc": {"balance_cents": amount_cents}}, upsert=True)
    _record(owner_id, "refund", amount_cents, errand_id, "Cancellation refund")
    return get_balance(owner_id)


def set_email(owner_id, email):
    """Remember where to send this business's wallet alerts."""
    if email:
        _wallets().update_one({"business_owner_id": owner_id},
                              {"$set": {"email": email}}, upsert=True)


def _email(owner_id):
    w = _wallets().find_one({"business_owner_id": owner_id})
    return (w or {}).get("email")


def get_email(owner_id):
    """Public accessor for the business's alert email (falls back to the default)."""
    return _email(owner_id) or DEFAULT_ALERT_EMAIL


def _topup_token(owner_id, amount_cents):
    """HMAC-sign a one-click top-up link so it can't be forged or tampered with."""
    msg = f"{owner_id}:{amount_cents}".encode()
    return hmac.new(TOPUP_LINK_SECRET.encode(), msg, hashlib.sha256).hexdigest()


def verify_topup_token(owner_id, amount_cents, token):
    """Constant-time check of a top-up link's signature."""
    return hmac.compare_digest(_topup_token(owner_id, amount_cents), token or "")


def _topup_link(owner_id, amount_cents, answer):
    q = urllib.parse.urlencode({"owner": owner_id, "amount": amount_cents,
                                "answer": answer, "token": _topup_token(owner_id, amount_cents)})
    return f"{PORTAL_BASE}/v1/wallet/confirm-topup?{q}"


def _send_low_balance_email(owner_id, to_email, balance):
    """Send the low-balance alert with one-click Yes/No top-up buttons.

    If EMAIL_HOST_USER/PASSWORD are set (e.g. a Gmail App Password), a real email is
    sent; otherwise Django's console backend prints it to the server log. The Yes/No
    links are HMAC-signed so a click can only top up this business's own wallet.
    """
    from django.conf import settings
    from django.core.mail import EmailMessage
    amount = TOPUP_OFFER_CENTS
    yes_url = _topup_link(owner_id, amount, "yes")
    no_url = _topup_link(owner_id, amount, "no")
    subject = "⚠ Your Aerrand wallet is low — top up now?"
    html = f"""\
<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#1a1a1a;max-width:460px">
  <p>Hi,</p>
  <p>Your Aerrand wallet has dropped to <b>${balance:.2f}</b>, below the
     ${LOW_BALANCE_CENTS / 100:.2f} low-balance threshold. New deliveries are paused until you add funds.</p>
  <p><b>Would you like to top up ${amount / 100:.2f} now?</b></p>
  <p style="margin:22px 0">
    <a href="{yes_url}" style="background:#5b2fd6;color:#fff;padding:11px 24px;border-radius:8px;text-decoration:none;font-weight:bold;margin-right:10px">Yes, top up ${amount / 100:.0f}</a>
    <a href="{no_url}" style="background:#eee;color:#333;padding:11px 24px;border-radius:8px;text-decoration:none">No, not now</a>
  </p>
  <p style="color:#888;font-size:12px">— The Aerrand team</p>
</div>"""
    from_addr = getattr(settings, "DEFAULT_FROM_EMAIL", "alerts@aerrand.dev")
    msg = EmailMessage(subject, html, from_addr, [to_email])
    msg.content_subtype = "html"
    msg.send(fail_silently=True)


def send_topup_email(owner_id, amount_cents, new_balance_cents):
    """Email a confirmation whenever the business tops up the wallet."""
    from django.conf import settings
    from django.core.mail import EmailMessage
    to_email = get_email(owner_id)
    subject = "✅ Your Aerrand wallet was topped up"
    html = f"""\
<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#1a1a1a;max-width:460px">
  <p>Hi,</p>
  <p>Your Aerrand wallet was topped up by <b>${amount_cents / 100:.2f}</b>.</p>
  <p>New balance: <b>${new_balance_cents / 100:.2f}</b>.</p>
  <p style="color:#888;font-size:12px">— The Aerrand team</p>
</div>"""
    from_addr = getattr(settings, "DEFAULT_FROM_EMAIL", "alerts@aerrand.dev")
    msg = EmailMessage(subject, html, from_addr, [to_email])
    msg.content_subtype = "html"
    msg.send(fail_silently=True)


def check_low_balance(owner_id):
    """After a charge: if the wallet is now low, email the business.

    Returns a summary (for the demo / API), or None if the balance is still healthy.
    The wallet is NOT auto-reloaded — new deliveries stay blocked (see the booking
    guard in views.py) until the business tops up manually.
    """
    balance = get_balance(owner_id)
    if balance >= LOW_BALANCE_CENTS:
        return None
    before = round(balance / 100, 2)
    email = get_email(owner_id)
    _send_low_balance_email(owner_id, email, before)
    return {"triggered": True, "emailed": email, "balance": before}


def transactions(owner_id, limit=25):
    rows = _txns().find({"business_owner_id": owner_id}).sort("at", -1).limit(limit)
    return [{
        "kind": r["kind"],
        "amount": round(r["amount_cents"] / 100, 2),
        "errand_id": r.get("errand_id"),
        "note": r.get("note", ""),
        "at": r["at"].isoformat(),
    } for r in rows]
