from __future__ import annotations


def format_brl(amount: float) -> str:
    """Formata número para padrão brasileiro sem o prefixo R$."""
    base = f"{amount:,.2f}"
    return base.replace(",", "_").replace(".", ",").replace("_", ".")


def parse_amount(value: str) -> float:
    """Converte valores monetários em texto para float.

    Exemplos aceitos:
    - 50
    - 50,75
    - 1.000
    - 1.000,50
    - 1000.50
    """
    text = (value or "").strip().replace(" ", "")
    if not text:
        raise ValueError("Valor vazio")

    has_comma = "," in text
    has_dot = "." in text

    if has_comma and has_dot:
        # Assume formato BR quando há os dois separadores: 1.234,56
        normalized = text.replace(".", "").replace(",", ".")
    elif has_comma:
        normalized = text.replace(",", ".")
    elif has_dot:
        # Se houver exatamente 3 dígitos após o ponto, assume milhar (1.000)
        integer, _, decimal = text.partition(".")
        if decimal.isdigit() and len(decimal) == 3:
            normalized = integer + decimal
        else:
            normalized = text
    else:
        normalized = text

    return float(normalized)