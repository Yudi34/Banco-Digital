from __future__ import annotations

from typing import Any

from flask import session

from atm import ATM
from money import parse_amount


def get_atm() -> ATM:
    return ATM()


def get_logged_in_user() -> str | None:
    username = session.get("username")
    if not username:
        return None

    atm = get_atm()
    if username not in atm.data["users"]:
        session.pop("username", None)
        return None

    return username


def _parse_entry(entry: Any) -> dict[str, Any]:
    """Normaliza entradas do histórico — suporta formato dict (novo) e string (legado)."""
    if isinstance(entry, dict):
        return entry

    # Formato legado: "Depósito: +R$200.00" ou "Saque: -R$100.00"
    is_deposit = entry.startswith("Depósito")
    raw = entry.split("R$", maxsplit=1)[-1].strip()
    try:
        amount = parse_amount(raw)
    except ValueError:
        amount = 0.0

    return {
        "type": "deposit" if is_deposit else "withdraw",
        "amount": amount,
        "description": entry,
        "timestamp": None,
    }


def build_dashboard_data(username: str) -> dict[str, Any]:
    atm = get_atm()
    atm.current_user = username

    balance = atm.get_balance()
    history = list(atm.get_history())
    account_info = atm.get_account_info()

    entries: list[dict[str, Any]] = []
    total_deposits = 0.0
    total_withdraws = 0.0

    for index, raw_entry in enumerate(reversed(history), start=1):
        entry = _parse_entry(raw_entry)
        tx_type = entry.get("type", "withdraw")
        amount = entry.get("amount", 0.0)

        is_credit = tx_type in ("deposit", "transfer_in")

        if is_credit:
            total_deposits += amount
        else:
            total_withdraws += amount

        label_map = {
            "deposit": "Depósito",
            "withdraw": "Saque",
            "transfer_out": "Transferência enviada",
            "transfer_in": "Transferência recebida",
        }

        entries.append(
            {
                "id": index,
                "label": label_map.get(tx_type, "Movimentação"),
                "amount": amount,
                "kind": "deposit" if is_credit else "withdraw",
                "description": entry.get("description", ""),
                "timestamp": entry.get("timestamp"),
                "tx_type": tx_type,
            }
        )

    return {
        "balance": balance,
        "entries": entries,
        "total_deposits": total_deposits,
        "total_withdraws": total_withdraws,
        "count": len(entries),
        "account_info": account_info,
        "transaction_limits": atm.get_transaction_limits(),
    }
