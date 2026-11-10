"""Wallet statement export (CSV) and low-balance detection.

Turns a business's wallet transaction history into a downloadable CSV statement/invoice,
and flags when the balance has dropped below a top-up threshold so the business can
reload before a booking fails for insufficient funds.
"""
import csv
import io

LOW_BALANCE_CENTS = 2000  # warn once the balance drops below $20.00


def is_low(balance_cents, threshold_cents=LOW_BALANCE_CENTS):
    """True when the wallet balance is below the low-balance threshold."""
    return int(balance_cents) < int(threshold_cents)


def to_csv(transactions):
    """Render wallet transactions (from wallet.transactions()) as CSV text."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["date", "type", "amount_cad", "errand_id", "note"])
    for t in transactions:
        writer.writerow([
            t.get("at", ""),
            t.get("kind", ""),
            t.get("amount", ""),
            t.get("errand_id") or "",
            t.get("note", ""),
        ])
    return buf.getvalue()
