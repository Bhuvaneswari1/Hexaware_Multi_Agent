"""CSV read models and a transactional, simulated refund ledger."""
import csv
import sqlite3
from pathlib import Path
from common.config import DATA


def rows(name: str) -> list[dict]:
    with (DATA / name).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def order_for(customer_id: str, order_id: str) -> dict:
    found = next((r for r in rows('orders.csv') if r['order_id'] == order_id), None)
    if not found or found['customer_id'] != customer_id:
        raise PermissionError('Order not found for this customer.')
    return found


def billing_facts(customer_id: str, order_id: str) -> dict:
    order_for(customer_id, order_id)
    payments = [r for r in rows('payments.csv')
                if r['order_id'] == order_id and r['status'] == 'captured']
    # Training contract: first captured payment is valid; identical extras are duplicates.
    amounts = [int(r['amount_inr']) for r in payments]
    duplicate = sum(amounts[1:]) if amounts and len(set(amounts)) == 1 else 0
    return {'captured_payments': len(payments), 'duplicate_amount_inr': duplicate,
            'payment_ids': [r['payment_id'] for r in payments]}


def faq(query: str) -> list[dict]:
    words = set(query.lower().split())
    scored = sorted(rows('knowledge.csv'),
                    key=lambda r: len(words & set((r['topic'] + ' ' + r['text']).lower().split())),
                    reverse=True)
    return scored[:2]


def simulate_refund(db: Path, *, role: str, customer_id: str, order_id: str,
                    amount: int, approved: bool) -> dict:
    """Only application-controlled Billing can execute. Never moves real money."""
    if role != 'billing':
        raise PermissionError('Only Billing may execute the refund tool.')
    maximum = billing_facts(customer_id, order_id)['duplicate_amount_inr']
    if not 0 < amount <= maximum:
        raise ValueError('Refund must be positive and within the verified duplicate charge.')
    if amount > 1000 and not approved:
        raise PermissionError('Human approval is required above INR 1000.')
    with sqlite3.connect(db) as con:
        con.execute('CREATE TABLE IF NOT EXISTS refunds (order_id TEXT PRIMARY KEY, amount INTEGER)')
        existing = con.execute('SELECT amount FROM refunds WHERE order_id=?', (order_id,)).fetchone()
        if existing:
            if existing[0] != amount:
                raise ValueError('An existing simulated refund has a different amount; escalate.')
            return {'status': 'already_simulated', 'amount_inr': amount}
        con.execute('INSERT INTO refunds VALUES (?,?)', (order_id, amount))
    return {'status': 'simulated', 'amount_inr': amount}
