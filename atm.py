import json
import os
import random
from datetime import datetime
from typing import Tuple, List, Dict, Any

from money import format_brl
from werkzeug.security import check_password_hash, generate_password_hash


class ATM:
    """ATM system with user authentication and transactions."""

    def __init__(self, db_path: str = "database.json") -> None:
        self.db_path = db_path
        self.data = self._load_database()
        self._migrate_plaintext_passwords()
        self._migrate_user_defaults()
        self.current_user: str | None = None

    # ------------------------- BANCO DE DADOS -------------------------
    def _load_database(self) -> Dict[str, Any]:
        """Carrega o arquivo JSON do banco de dados."""
        if not os.path.exists(self.db_path):
            return {"users": {}}

        with open(self.db_path, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {"users": {}}

    def _save_database(self) -> None:
        """Salva alterações no arquivo JSON."""
        with open(self.db_path, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)

    def _is_password_hashed(self, password: str) -> bool:
        return password.startswith(("pbkdf2:", "scrypt:", "bcrypt:"))

    def _migrate_plaintext_passwords(self) -> None:
        """Converte senhas legadas em texto puro para hash."""
        users = self.data.get("users", {})
        updated = False

        for user in users.values():
            stored = user.get("password")
            if isinstance(stored, str) and not self._is_password_hashed(stored):
                user["password"] = generate_password_hash(stored)
                updated = True

        if updated:
            self._save_database()

    def _default_limits(self) -> Dict[str, float]:
        return {
            "deposit": 50_000.0,
            "withdraw": 5_000.0,
            "transfer": 10_000.0,
        }

    def _migrate_user_defaults(self) -> None:
        """Garante defaults de segurança e limites em contas legadas."""
        users = self.data.get("users", {})
        defaults = self._default_limits()
        updated = False

        for user in users.values():
            limits = user.get("limits")
            if not isinstance(limits, dict):
                user["limits"] = defaults.copy()
                updated = True
                continue

            for key, default_value in defaults.items():
                raw_value = limits.get(key)
                if not isinstance(raw_value, (int, float)) or raw_value <= 0:
                    limits[key] = default_value
                    updated = True
                else:
                    limits[key] = float(raw_value)

        if updated:
            self._save_database()

    def _validate_password_strength(self, password: str) -> str | None:
        if len(password) < 8:
            return "A senha deve ter pelo menos 8 caracteres."

        has_letter = any(ch.isalpha() for ch in password)
        has_number = any(ch.isdigit() for ch in password)

        if not has_letter or not has_number:
            return "A senha deve conter pelo menos 1 letra e 1 número."

        return None

    # ------------------------- MÉTODOS DE CONTA -------------------------
    def create_account(self, username: str, password: str) -> Tuple[bool, str]:
        """Cria uma nova conta de usuário."""
        if not username or not password:
            return False, "Usuário e senha não podem estar vazios."

        if len(username) < 3:
            return False, "O nome de usuário deve ter pelo menos 3 caracteres."

        password_error = self._validate_password_strength(password)
        if password_error:
            return False, password_error

        if username in self.data["users"]:
            return False, "Usuário já existe."

        self.data["users"][username] = {
            "password": generate_password_hash(password),
            "balance": 0.0,
            "history": [],
            "agency": "0001",
            "account_number": self._generate_account_number(),
            "limits": self._default_limits(),
        }
        self._save_database()
        return True, "Conta criada com sucesso!"

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """Realiza o login do usuário."""
        user = self.data["users"].get(username)

        if not user:
            return False, "Usuário não encontrado."

        stored = user["password"]
        # Suporte a senhas legadas (texto puro) e novas (hash werkzeug)
        is_hashed = self._is_password_hashed(stored)
        valid = check_password_hash(stored, password) if is_hashed else stored == password

        if not valid:
            return False, "Senha incorreta."

        self.current_user = username
        return True, "Login realizado com sucesso!"

    def change_password(self, current_password: str, new_password: str) -> Tuple[bool, str]:
        """Altera a senha do usuário autenticado."""
        if not self.current_user:
            return False, "Usuário não autenticado."

        password_error = self._validate_password_strength(new_password)
        if password_error:
            return False, password_error

        user = self._current_user_data()
        stored = user["password"]
        is_hashed = self._is_password_hashed(stored)
        valid_current = (
            check_password_hash(stored, current_password) if is_hashed else stored == current_password
        )

        if not valid_current:
            return False, "Senha atual incorreta."

        if current_password == new_password:
            return False, "A nova senha deve ser diferente da senha atual."

        user["password"] = generate_password_hash(new_password)
        self._save_database()
        return True, "Senha atualizada com sucesso!"

    def reset_password(self, username: str, new_password: str) -> Tuple[bool, str]:
        """Redefine a senha a partir da tela inicial."""
        user = self.data["users"].get(username)
        if not user:
            return False, "Usuário não encontrado."

        password_error = self._validate_password_strength(new_password)
        if password_error:
            return False, password_error

        stored = user["password"]
        is_hashed = self._is_password_hashed(stored)
        same_password = check_password_hash(stored, new_password) if is_hashed else stored == new_password
        if same_password:
            return False, "A nova senha deve ser diferente da senha atual."

        user["password"] = generate_password_hash(new_password)
        self._save_database()
        return True, "Senha redefinida com sucesso!"

    def get_account_info(self) -> Dict[str, str]:
        """Retorna agência e número de conta do usuário."""
        user = self._current_user_data()
        return {
            "agency": user.get("agency", "0001"),
            "account_number": user.get("account_number", "00000-0"),
        }

    def get_transaction_limits(self) -> Dict[str, float]:
        """Retorna os limites por operação do usuário."""
        user = self._current_user_data()
        limits = user.get("limits", {})
        defaults = self._default_limits()

        return {
            "deposit": float(limits.get("deposit", defaults["deposit"])),
            "withdraw": float(limits.get("withdraw", defaults["withdraw"])),
            "transfer": float(limits.get("transfer", defaults["transfer"])),
        }

    def update_transaction_limits(
        self,
        current_password: str,
        deposit_limit: float,
        withdraw_limit: float,
        transfer_limit: float,
    ) -> Tuple[bool, str]:
        """Atualiza limites de transação após validar senha atual."""
        if not self.current_user:
            return False, "Usuário não autenticado."

        user = self._current_user_data()
        stored = user["password"]
        is_hashed = self._is_password_hashed(stored)
        valid_current = (
            check_password_hash(stored, current_password) if is_hashed else stored == current_password
        )
        if not valid_current:
            return False, "Senha atual incorreta."

        raw_limits = {
            "depósito": deposit_limit,
            "saque": withdraw_limit,
            "transferência": transfer_limit,
        }

        for label, value in raw_limits.items():
            if value <= 0:
                return False, f"O limite de {label} deve ser maior que zero."
            if value > 1_000_000:
                return False, f"O limite de {label} não pode ultrapassar R$ 1.000.000,00."

        user["limits"] = {
            "deposit": round(deposit_limit, 2),
            "withdraw": round(withdraw_limit, 2),
            "transfer": round(transfer_limit, 2),
        }
        self._save_database()

        return True, "Limites de transação atualizados com sucesso."

    # ------------------------- TRANSAÇÕES -------------------------
    def get_balance(self) -> float:
        """Retorna o saldo do usuário."""
        return self._current_user_data()["balance"]

    def deposit(self, amount: float) -> Tuple[bool, str]:
        """Realiza um depósito."""
        if amount <= 0:
            return False, "O valor deve ser maior que zero."

        limits = self.get_transaction_limits()
        if amount > limits["deposit"]:
            return False, f"Limite de depósito por operação: R$ {format_brl(limits['deposit'])}."

        user = self._current_user_data()
        user["balance"] = round(user["balance"] + amount, 2)
        amount_label = format_brl(amount)
        user["history"].append({
            "type": "deposit",
            "amount": amount,
            "description": f"Depósito de R$ {amount_label}",
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
        })

        self._save_database()
        return True, f"Depósito de R$ {amount_label} realizado com sucesso!"

    def withdraw(self, amount: float) -> Tuple[bool, str]:
        """Realiza um saque."""
        user = self._current_user_data()

        if amount <= 0:
            return False, "O valor deve ser maior que zero."

        if amount > user["balance"]:
            return False, "Saldo insuficiente."

        limits = self.get_transaction_limits()
        if amount > limits["withdraw"]:
            return False, f"Limite de saque por operação: R$ {format_brl(limits['withdraw'])}."

        user["balance"] = round(user["balance"] - amount, 2)
        amount_label = format_brl(amount)
        user["history"].append({
            "type": "withdraw",
            "amount": amount,
            "description": f"Saque de R$ {amount_label}",
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
        })

        self._save_database()
        return True, f"Saque de R$ {amount_label} realizado com sucesso!"

    def transfer(self, target_username: str, amount: float) -> Tuple[bool, str]:
        """Realiza uma transferência entre contas."""
        if self.current_user == target_username:
            return False, "Não é possível transferir para a própria conta."

        if target_username not in self.data["users"]:
            return False, "Conta de destino não encontrada."

        if amount <= 0:
            return False, "O valor deve ser maior que zero."

        limits = self.get_transaction_limits()
        if amount > limits["transfer"]:
            return False, f"Limite de transferência por operação: R$ {format_brl(limits['transfer'])}."

        sender = self._current_user_data()

        if amount > sender["balance"]:
            return False, "Saldo insuficiente."

        receiver = self.data["users"][target_username]
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")

        sender["balance"] = round(sender["balance"] - amount, 2)
        sender["history"].append({
            "type": "transfer_out",
            "amount": amount,
            "description": f"Transferência enviada para {target_username}",
            "timestamp": timestamp,
        })

        receiver["balance"] = round(receiver["balance"] + amount, 2)
        receiver["history"].append({
            "type": "transfer_in",
            "amount": amount,
            "description": f"Transferência recebida de {self.current_user}",
            "timestamp": timestamp,
        })

        self._save_database()
        amount_label = format_brl(amount)
        return True, f"Transferência de R$ {amount_label} para {target_username} realizada!"

    # ------------------------- UTILIDADES -------------------------
    def get_history(self) -> List[Any]:
        """Retorna o histórico de transações do usuário."""
        return self._current_user_data()["history"]

    def logout(self) -> None:
        """Desloga o usuário atual."""
        self.current_user = None

    def _current_user_data(self) -> Dict[str, Any]:
        """Retorna os dados do usuário logado."""
        return self.data["users"][self.current_user]

    def _generate_account_number(self) -> str:
        """Gera um número de conta único no formato XXXXX-D."""
        existing = {
            u.get("account_number") for u in self.data["users"].values()
        }
        while True:
            number = f"{random.randint(10000, 99999)}-{random.randint(0, 9)}"
            if number not in existing:
                return number