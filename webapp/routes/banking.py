from flask import flash, redirect, render_template, request, url_for

from money import parse_amount

from .shared import bp
from ..services import build_dashboard_data, get_atm, get_logged_in_user


@bp.get("/dashboard")
def dashboard():
    username = get_logged_in_user()
    if not username:
        flash("Faça login para continuar.", "error")
        return redirect(url_for("bank.index"))

    dashboard_data = build_dashboard_data(username)
    return render_template(
        "dashboard.html",
        title="Painel | NovaConta",
        username=username,
        balance=dashboard_data["balance"],
        entries=dashboard_data["entries"],
        total_deposits=dashboard_data["total_deposits"],
        total_withdraws=dashboard_data["total_withdraws"],
        transaction_count=dashboard_data["count"],
        account_info=dashboard_data["account_info"],
    )


@bp.get("/statement")
def statement():
    username = get_logged_in_user()
    if not username:
        flash("Faça login para continuar.", "error")
        return redirect(url_for("bank.index"))

    dashboard_data = build_dashboard_data(username)
    return render_template(
        "statement.html",
        title="Extrato | NovaConta",
        username=username,
        entries=dashboard_data["entries"],
        transaction_count=dashboard_data["count"],
        balance=dashboard_data["balance"],
        total_deposits=dashboard_data["total_deposits"],
        total_withdraws=dashboard_data["total_withdraws"],
    )


@bp.get("/profile")
def profile():
    username = get_logged_in_user()
    if not username:
        flash("Faça login para continuar.", "error")
        return redirect(url_for("bank.index"))

    dashboard_data = build_dashboard_data(username)
    return render_template(
        "profile.html",
        title="Perfil | NovaConta",
        username=username,
        account_info=dashboard_data["account_info"],
        transaction_limits=dashboard_data["transaction_limits"],
    )


@bp.post("/transaction")
def transaction():
    username = get_logged_in_user()
    if not username:
        flash("Sessão expirada. Faça login novamente.", "error")
        return redirect(url_for("bank.index"))

    transaction_type = request.form.get("type", "")
    selected_tab = "ops-withdraw" if transaction_type == "withdraw" else "ops-deposit"
    raw_amount = request.form.get("amount", "0").strip()

    try:
        amount = parse_amount(raw_amount)
    except ValueError:
        flash("Valor inválido.", "error")
        return redirect(url_for("bank.dashboard", tab=selected_tab))

    atm = get_atm()
    atm.current_user = username

    if transaction_type == "deposit":
        success, msg = atm.deposit(amount)
    elif transaction_type == "withdraw":
        success, msg = atm.withdraw(amount)
    else:
        success, msg = False, "Transação inválida."

    flash(msg, "success" if success else "error")
    return redirect(url_for("bank.dashboard", tab=selected_tab))


@bp.post("/transfer")
def transfer():
    username = get_logged_in_user()
    if not username:
        flash("Sessão expirada. Faça login novamente.", "error")
        return redirect(url_for("bank.index"))

    target = request.form.get("target", "").strip()
    raw_amount = request.form.get("amount", "0").strip()

    try:
        amount = parse_amount(raw_amount)
    except ValueError:
        flash("Valor inválido.", "error")
        return redirect(url_for("bank.dashboard", tab="ops-transfer"))

    atm = get_atm()
    atm.current_user = username
    success, msg = atm.transfer(target, amount)

    flash(msg, "success" if success else "error")
    return redirect(url_for("bank.dashboard", tab="ops-transfer"))
