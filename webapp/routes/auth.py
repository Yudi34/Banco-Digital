import re
import time

from flask import flash, redirect, render_template, request, session, url_for

from money import parse_amount
from .shared import bp
from ..services import get_atm, get_logged_in_user


USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")
MAX_LOGIN_ATTEMPTS = 5
LOGIN_BLOCK_SECONDS = 300


def _validate_username(username: str) -> bool:
    return bool(USERNAME_PATTERN.fullmatch(username))


def _check_login_block() -> tuple[bool, int]:
    now = time.time()
    attempts = session.get("login_attempts", [])
    recent_attempts = [ts for ts in attempts if isinstance(ts, (int, float)) and now - ts < LOGIN_BLOCK_SECONDS]
    session["login_attempts"] = recent_attempts

    if len(recent_attempts) >= MAX_LOGIN_ATTEMPTS:
        wait_seconds = int(LOGIN_BLOCK_SECONDS - (now - recent_attempts[0]))
        return True, max(wait_seconds, 1)

    return False, 0


def _register_login_failure() -> None:
    attempts = session.get("login_attempts", [])
    if not isinstance(attempts, list):
        attempts = []
    attempts.append(time.time())
    session["login_attempts"] = attempts


@bp.get("/")
def index():
    if get_logged_in_user():
        return redirect(url_for("bank.dashboard"))
    return render_template("index.html", title="NovaConta | Banco")


@bp.post("/register")
def register():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not _validate_username(username):
        flash("Usuário inválido. Use 3-30 caracteres: letras, números, ponto, hífen ou underscore.", "error")
        return redirect(url_for("bank.index"))

    atm = get_atm()
    success, msg = atm.create_account(username, password)
    flash(msg, "success" if success else "error")
    return redirect(url_for("bank.index"))


@bp.post("/login")
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    blocked, wait_seconds = _check_login_block()
    if blocked:
        flash(f"Muitas tentativas. Tente novamente em {wait_seconds}s.", "error")
        return redirect(url_for("bank.index"))

    if not _validate_username(username):
        flash("Usuário ou senha inválidos.", "error")
        return redirect(url_for("bank.index"))

    atm = get_atm()
    success, msg = atm.login(username, password)
    if success:
        session.clear()
        session["username"] = username
        session.permanent = True
        flash("Sessão iniciada com sucesso.", "success")
        return redirect(url_for("bank.dashboard"))

    _register_login_failure()
    flash("Usuário ou senha inválidos.", "error")
    return redirect(url_for("bank.index"))


@bp.post("/password/change")
def change_password():
    username = get_logged_in_user()
    if not username:
        flash("Sessão expirada. Faça login novamente.", "error")
        return redirect(url_for("bank.index"))

    current_password = request.form.get("current_password", "").strip()
    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    if not current_password or not new_password or not confirm_password:
        flash("Preencha todos os campos de senha.", "error")
        return redirect(url_for("bank.profile", tab="security"))

    if new_password != confirm_password:
        flash("A confirmação da senha não confere.", "error")
        return redirect(url_for("bank.profile", tab="security"))

    atm = get_atm()
    atm.current_user = username
    success, msg = atm.change_password(current_password, new_password)
    flash(msg, "success" if success else "error")
    return redirect(url_for("bank.profile", tab="security"))


@bp.post("/password/reset")
def reset_password():
    username = get_logged_in_user()
    if not username:
        flash("Por segurança, redefina sua senha na área de perfil após login.", "error")
        return redirect(url_for("bank.index"))

    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    if not new_password or not confirm_password:
        flash("Preencha os dois campos da nova senha.", "error")
        return redirect(url_for("bank.profile", tab="security"))

    if new_password != confirm_password:
        flash("A confirmação da senha não confere.", "error")
        return redirect(url_for("bank.profile", tab="security"))

    atm = get_atm()
    success, msg = atm.reset_password(username, new_password)
    flash(msg, "success" if success else "error")
    return redirect(url_for("bank.profile", tab="security"))


@bp.post("/profile/limits")
def update_limits():
    username = get_logged_in_user()
    if not username:
        flash("Sessão expirada. Faça login novamente.", "error")
        return redirect(url_for("bank.index"))

    current_password = request.form.get("current_password", "").strip()
    raw_deposit = request.form.get("deposit_limit", "").strip()
    raw_withdraw = request.form.get("withdraw_limit", "").strip()
    raw_transfer = request.form.get("transfer_limit", "").strip()

    if not current_password or not raw_deposit or not raw_withdraw or not raw_transfer:
        flash("Preencha senha atual e todos os limites.", "error")
        return redirect(url_for("bank.profile", tab="limits"))

    try:
        deposit_limit = parse_amount(raw_deposit)
        withdraw_limit = parse_amount(raw_withdraw)
        transfer_limit = parse_amount(raw_transfer)
    except ValueError:
        flash("Informe limites válidos.", "error")
        return redirect(url_for("bank.profile", tab="limits"))

    atm = get_atm()
    atm.current_user = username
    success, msg = atm.update_transaction_limits(
        current_password,
        deposit_limit,
        withdraw_limit,
        transfer_limit,
    )
    flash(msg, "success" if success else "error")
    return redirect(url_for("bank.profile", tab="limits"))


@bp.post("/logout")
def logout():
    session.clear()
    flash("Logout realizado.", "success")
    return redirect(url_for("bank.index"))
