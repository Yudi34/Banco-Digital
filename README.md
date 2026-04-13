# Banco Digital 2.0 (Flask)

Aplicativo bancario web feito com Flask para estudos e portfolio.

Esta e a versao 2.0 do projeto, com evolucao visual, melhorias de acessibilidade,
nova organizacao de rotas e experiencia de uso mais completa que a versao base.

## O que mudou na 2.0

- Novo visual com layout mais moderno e responsivo
- Dashboard, perfil e extrato redesenhados
- Filtros no extrato por tipo de movimentacao
- Melhorias de acessibilidade, foco por teclado e contraste alto
- Feedback visual de carregamento nos formularios
- Separacao das rotas em modulos de autenticacao e operacoes bancarias
- Melhor tratamento de valores monetarios com parser dedicado

## Funcionalidades

- Criacao de conta
- Login e logout
- Deposito e saque
- Extrato de transacoes
- Dashboard com resumo financeiro
- Perfil com alteracao de senha e limites por operacao
- Transferencia entre usuarios

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

O projeto ja esta preparado com `render.yaml` e `Procfile`.

Passos:

1. Entre em https://render.com e conecte sua conta GitHub.
2. Clique em New + > Web Service.
3. Selecione o repositorio `Banco-Digital`.
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
- `webapp/`: rotas e servicos da camada web
- `templates/`: telas HTML
- `static/`: estilos CSS
- `atm.py`: logica de conta e transacoes
- `money.py`: parse e formatacao de valores monetarios

## Versoes

- `versao-antiga`: implementacao base do projeto
- `versao-2-0`: versao atual com melhorias visuais e estruturais
- `v2.0.0`: tag da release 2.0


