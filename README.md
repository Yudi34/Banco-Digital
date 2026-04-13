# Banco Digital 2.0 (Flask)

Aplicativo bancário web feito com Flask para estudos e portfólio.

Esta é a versão 2.0 do projeto, com evolução visual, melhorias de acessibilidade,
nova organização de rotas e uma experiência de uso mais completa do que a versão base.

## O que mudou na 2.0

- Novo visual com layout mais moderno e responsivo
- Dashboard, perfil e extrato redesenhados
- Filtros no extrato por tipo de movimentação
- Melhorias de acessibilidade, foco por teclado e contraste alto
- Feedback visual de carregamento nos formulários
- Separação das rotas em módulos de autenticação e operações bancárias
- Melhor tratamento de valores monetários com parser dedicado

## Melhorias de segurança

- Proteção contra CSRF nos formulários
- Cookies de sessão com políticas mais seguras
- Cabeçalhos HTTP de segurança para proteção adicional da aplicação
- Hash de senha com migração de credenciais antigas em texto puro
- Validação de força mínima de senha
- Bloqueio temporário após múltiplas tentativas de login
- Confirmação por senha atual em operações sensíveis

## Funcionalidades

- Criação de conta
- Login e logout
- Depósito e saque
- Extrato de transações
- Dashboard com resumo financeiro
- Perfil com alteração de senha e limites por operação
- Transferência entre usuários

## Tecnologias

- Python 3
- Flask
- HTML + CSS
- Jinja2

## Como rodar localmente

1. Abra o terminal na pasta do projeto.
2. Execute:

```powershell
& ".\.venv-1\Scripts\python.exe" .\main.py
```

3. Abra no navegador: http://127.0.0.1:5000

## Deploy no Render

O projeto já está preparado com `render.yaml` e `Procfile`.

Passos:

1. Entre em https://render.com e conecte sua conta GitHub.
2. Clique em New + > Web Service.
3. Selecione o repositório `Banco-Digital`.
4. Confirme os comandos:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:app`
5. Clique em Create Web Service.

## Deploy no Railway

1. Entre em https://railway.app.
2. Clique em New Project > Deploy from GitHub Repo.
3. Selecione `Banco-Digital`.
4. O Railway vai usar o `Procfile` automaticamente.

## Estrutura principal

- `main.py`: ponto de entrada da aplicação
- `webapp/`: rotas e serviços da camada web
- `templates/`: telas HTML
- `static/`: estilos CSS
- `atm.py`: lógica de conta e transações
- `money.py`: parse e formatação de valores monetários

## Versões

- `versao-antiga`: implementação base do projeto
- `versao-2-0`: versão atual com melhorias visuais e estruturais
- `v2.0.0`: tag da release 2.0


