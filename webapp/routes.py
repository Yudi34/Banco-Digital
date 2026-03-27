from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from .services import build_dashboard_data, get_atm, get_logged_in_user


bp = Blueprint("bank", __name__)


@bp.get("/")
def index():
    if get_logged_in_user():
        return redirect(url_for("bank.dashboard"))
    return render_template("index.html", title="NovaConta | Banco")


@bp.post("/register")
def register():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    atm = get_atm()
    _, msg = atm.create_account(username, password)
    flash(msg)
    return redirect(url_for("bank.index"))


@bp.post("/login")
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    atm = get_atm()
    success, msg = atm.login(username, password)
    if success:
        session["username"] = username
        flash("Sessão iniciada com sucesso.")
        return redirect(url_for("bank.dashboard"))

    flash(msg)
    return redirect(url_for("bank.index"))


@bp.get("/dashboard")
def dashboard():
    username = get_logged_in_user()
    if not username:
        flash("Faça login para continuar.")
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
    )


@bp.post("/transaction")
def transaction():
    username = get_logged_in_user()
    if not username:
        flash("Sessão expirada. Faça login novamente.")
        return redirect(url_for("bank.index"))

    transaction_type = request.form.get("type", "")
    raw_amount = request.form.get("amount", "0").strip().replace(",", ".")

    try:
        amount = float(raw_amount)
    except ValueError:
        flash("Valor inválido.")
        return redirect(url_for("bank.dashboard"))

    atm = get_atm()
    atm.current_user = username

    if transaction_type == "deposit":
        _, msg = atm.deposit(amount)
    elif transaction_type == "withdraw":
        _, msg = atm.withdraw(amount)
    else:
        msg = "Transação inválida."

    flash(msg)
    return redirect(url_for("bank.dashboard"))


@bp.post("/logout")
def logout():
    session.pop("username", None)
    flash("Logout realizado.")
    return redirect(url_for("bank.index"))
