import json
import os
from typing import Tuple, List, Dict, Any


class ATM:
    """ATM system with user authentication and transactions."""

    def __init__(self, db_path: str = "database.json") -> None:
        self.db_path = db_path
        self.data = self._load_database()
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
            json.dump(self.data, file, indent=4)

    # ------------------------- MÉTODOS DE CONTA -------------------------
    def create_account(self, username: str, password: str) -> Tuple[bool, str]:
        """Cria uma nova conta de usuário."""
        if not username or not password:
            return False, "Usuário e senha não podem estar vazios."

        if username in self.data["users"]:
            return False, "Usuário já existe."

        self.data["users"][username] = {
            "password": password,
            "balance": 0.0,
            "history": []
        }
        self._save_database()
        return True, "Conta criada com sucesso!"

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """Realiza o login do usuário."""
        user = self.data["users"].get(username)

        if not user:
            return False, "Usuário não encontrado."

        if user["password"] != password:
            return False, "Senha incorreta."

        self.current_user = username
        return True, "Login realizado com sucesso!"

    # ------------------------- TRANSAÇÕES -------------------------
    def get_balance(self) -> float:
        """Retorna o saldo do usuário."""
        return self._current_user_data()["balance"]

    def deposit(self, amount: float) -> Tuple[bool, str]:
        """Realiza um depósito."""
        if amount <= 0:
            return False, "O valor deve ser maior que zero."

        user = self._current_user_data()
        user["balance"] += amount
        user["history"].append(f"Depósito: +R${amount:.2f}")

        self._save_database()
        return True, "Depósito realizado com sucesso!"

    def withdraw(self, amount: float) -> Tuple[bool, str]:
        """Realiza um saque."""
        user = self._current_user_data()

        if amount <= 0:
            return False, "O valor deve ser maior que zero."

        if amount > user["balance"]:
            return False, "Saldo insuficiente."

        user["balance"] -= amount
        user["history"].append(f"Saque: -R${amount:.2f}")

        self._save_database()
        return True, "Saque realizado com sucesso!"

    # ------------------------- UTILIDADES -------------------------
    def get_history(self) -> List[str]:
        """Retorna o histórico de transações do usuário."""
        return self._current_user_data()["history"]

    def logout(self) -> None:
        """Desloga o usuário atual."""
        self.current_user = None

    def _current_user_data(self) -> Dict[str, Any]:
        """Retorna os dados do usuário logado."""
        return self.data["users"][self.current_user]