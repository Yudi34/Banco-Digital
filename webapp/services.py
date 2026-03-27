from __future__ import annotations

from typing import Any

from flask import session

from atm import ATM


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


def _extract_amount(history_entry: str) -> float:
    marker = "R$"
    if marker not in history_entry:
        return 0.0

    raw = history_entry.split(marker, maxsplit=1)[1].strip().replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return 0.0


def build_dashboard_data(username: str) -> dict[str, Any]:
    atm = get_atm()
    atm.current_user = username

    balance = atm.get_balance()
    history = list(atm.get_history())

    entries: list[dict[str, Any]] = []
    total_deposits = 0.0
    total_withdraws = 0.0

    for index, entry in enumerate(reversed(history), start=1):
        is_deposit = entry.startswith("Depósito")
        amount = _extract_amount(entry)

        if is_deposit:
            total_deposits += amount
        else:
            total_withdraws += amount

        entries.append(
            {
                "id": index,
                "label": "Depósito" if is_deposit else "Saque",
                "amount": amount,
                "kind": "deposit" if is_deposit else "withdraw",
                "description": entry,
            }
        )

    return {
        "balance": balance,
        "entries": entries,
        "total_deposits": total_deposits,
        "total_withdraws": total_withdraws,
        "count": len(entries),
    }
