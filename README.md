# Lab 09 - APIs e Microsserviços no Render gratuito

Este projeto substitui o fluxo de Azure por Render, mantendo os exercícios do laboratório:

- **9.1:** Flask Hello World + API RESTful.
- **9.2:** API RESTful com FastAPI + Uvicorn.
- **9.3:** Flask Hello World publicado no Render.
- **9.4:** API RESTful Flask publicada no Render.

A estrutura também inclui:

- `render.yaml` para infraestrutura como código no Render.
- GitHub Actions para CI e CD.
- Script de bootstrap que cria os serviços no Render e configura automaticamente os secrets no GitHub usando `gh`.
- Coleção Postman pronta.

---

## 1. Pré-requisitos

Instale:

- Python 3.12+
- Git
- GitHub CLI (`gh`)
- Conta no Render
- Render API Key

Faça login no GitHub CLI:

```bash
gh auth login
```

---

## 2. Criar e subir o repositório no GitHub

Dentro da pasta do projeto:

```bash
git init
git add .
git commit -m "Lab 09 Render"
git branch -M main
gh repo create lab09-render-apis --public --source=. --remote=origin --push
```

Se preferir privado:

```bash
gh repo create lab09-render-apis --private --source=. --remote=origin --push
```

---

## 3. Rodar localmente

### Exercício 9.1 - Flask

```bash
cd exercicio_9_1_flask
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

No Windows PowerShell:

```powershell
cd exercicio_9_1_flask
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Acesse:

```text
http://127.0.0.1:5000/
http://127.0.0.1:5000/api/tasks
```

### Exercício 9.2 - FastAPI

```bash
cd exercicio_9_2_fastapi
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

No Windows PowerShell:

```powershell
cd exercicio_9_2_fastapi
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Acesse:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/tasks
```

---

## 4. Criar infra no Render e configurar secrets automaticamente

Exporte sua Render API Key:

```bash
export RENDER_API_KEY="sua_render_api_key"
```

No Windows PowerShell:

```powershell
$env:RENDER_API_KEY="sua_render_api_key"
```

Rode o bootstrap:

```bash
./scripts/bootstrap_render_infra.sh
```

Esse script faz o seguinte:

1. Confirma que você está logado no GitHub CLI.
2. Busca seus workspaces no Render.
3. Cria quatro Web Services no Render:
   - `lab09-ex91-flask-api`
   - `lab09-ex92-fastapi-api`
   - `lab09-ex93-flask-hello`
   - `lab09-ex94-flask-restful`
4. Dispara o deploy inicial.
5. Salva os IDs dos serviços em `.render/services.env`.
6. Configura automaticamente estes secrets no GitHub:
   - `RENDER_API_KEY`
   - `RENDER_OWNER_ID`
   - `RENDER_SERVICE_ID_EX91_FLASK`
   - `RENDER_SERVICE_ID_EX92_FASTAPI`
   - `RENDER_SERVICE_ID_EX93_HELLO_FLASK`
   - `RENDER_SERVICE_ID_EX94_FLASK_RESTFUL`

Se os nomes já existirem no Render, use um prefixo:

```bash
export SERVICE_PREFIX="gabriel"
./scripts/bootstrap_render_infra.sh
```

---

## 5. CI/CD

### CI

Arquivo:

```text
.github/workflows/ci.yml
```

Esse workflow roda `pytest` em todos os exercícios quando houver push ou pull request para `main`.

### CD

Arquivo:

```text
.github/workflows/deploy-render.yml
```

Esse workflow só dispara deploy no Render depois que o CI passa. Ele chama a API do Render para cada serviço.

### Validação do Blueprint

Arquivo:

```text
.github/workflows/infra-validate-render.yml
```

Esse workflow valida o `render.yaml` usando a API de validação do Render.

---

## 6. Comandos de produção no Render

### Flask

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
gunicorn --bind 0.0.0.0:$PORT app:app
```

### FastAPI

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## 7. Testar com Postman

Importe:

```text
postman/Lab09_Render.postman_collection.json
```

Ajuste as variáveis conforme as URLs reais geradas pelo Render:

```text
base_url_ex91
base_url_ex92
base_url_ex93
base_url_ex94
```

Exemplo:

```text
https://lab09-ex94-flask-restful.onrender.com
```

---

## 8. Entregáveis

### Exercício 9.1

- Link do código no GitHub.
- Print do PyCharm executando Flask.
- Print do browser em `/api/tasks`.
- Link ou arquivo da coleção Postman.

### Exercício 9.2

- Link do código no GitHub.
- Print do PyCharm executando Uvicorn.
- Print do browser em `/docs`.
- Link ou arquivo da coleção Postman.

### Exercício 9.3

- Link do repositório GitHub.
- Link da aplicação Flask Hello World online no Render.

### Exercício 9.4

- Link do código.
- Link do repositório.
- Link da API online no Render.
- Link ou arquivo da coleção Postman.

---

## 9. Endpoints principais

### Flask RESTful

```text
GET    /api/health
GET    /api/tasks
GET    /api/tasks/1
POST   /api/tasks
PUT    /api/tasks/1
DELETE /api/tasks/1
```

Body para POST:

```json
{
  "title": "Nova tarefa",
  "description": "Criada pelo Postman",
  "done": false
}
```

Body para PUT:

```json
{
  "title": "Tarefa atualizada",
  "description": "Atualizada pelo Postman",
  "done": true
}
```

---

## 10. Observação importante

As APIs usam armazenamento em memória. Em cada restart/deploy do Render, a lista de tarefas volta ao estado inicial. Isso é suficiente para o laboratório, mas em um projeto real você usaria banco de dados.
