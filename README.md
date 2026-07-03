# Banco Digital 2.0 (Flask)

Aplicação bancária web completa desenvolvida com Python e Flask.  
🌐 **Deploy ao vivo:** [banco-digital-1.onrender.com](https://banco-digital-1.onrender.com)

> ⚠️ O servidor pode demorar ~50s para carregar na primeira visita (plano gratuito Render)

## 📸 Screenshots

![Login](https://github.com/user-attachments/assets/a80e25b1-cf09-436d-a4a9-0468bda35c02)
![Dashboard](https://github.com/user-attachments/assets/87f1d89a-ffd1-40f3-aef6-1239a6d15aa3)

## ✨ Funcionalidades

- Cadastro e login/logout com autenticação segura
- Depósito, saque e transferência entre contas
- Extrato com filtros por tipo de movimentação
- Dashboard financeiro com resumo de entradas e saídas
- Perfil com alteração de senha e limites por operação

## 🔐 Segurança

- Proteção CSRF nos formulários
- Hash de senhas com SCRYPT
- Bloqueio temporário após múltiplas tentativas de login
- Cookies de sessão com políticas seguras
- Cabeçalhos HTTP de segurança

## 🛠️ Tecnologias

- Python 3 · Flask · Jinja2
- HTML · CSS
- Git · GitHub
- Deploy: Render

## ▶️ Como rodar localmente

```bash
git clone https://github.com/Yudi34/Banco-Digital
cd Banco-Digital
pip install -r requirements.txt
python main.py
```

Acesse: http://127.0.0.1:5000

## 👨‍💻 Autor

Pedro Yudi — [LinkedIn](https://linkedin.com/in/pedro-yudi-matsuoi-freire-3a799b349) · [GitHub](https://github.com/Yudi34)
