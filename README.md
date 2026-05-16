# Lab 09 - APIs e Microsservicos

Resolucao do Lab 09 de Engenharia de Software, com quatro exercicios de APIs em Flask/FastAPI, testes automatizados, colecao Postman, GitHub Actions e deploy no Render.

## Links publicados

| Exercicio | Tecnologia | URL | Endpoints principais |
| --- | --- | --- | --- |
| 9.1 | Flask API REST | https://lab09-ex91-flask-api.onrender.com | `/`, `/api/health`, `/api/tasks` |
| 9.2 | FastAPI API REST | https://lab09-ex92-fastapi-api.onrender.com | `/`, `/docs`, `/api/health`, `/api/tasks` |
| 9.3 | Flask Hello World | https://lab09-ex93-flask-hello.onrender.com | `/`, `/api/health` |
| 9.4 | Flask RESTful no Render | https://lab09-ex94-flask-restful.onrender.com | `/`, `/api/health`, `/api/tasks` |

## Estrutura

```text
.
|-- exercicio_9_1_flask/
|   |-- app.py
|   |-- requirements.txt
|   `-- test_app.py
|-- exercicio_9_2_fastapi/
|   |-- main.py
|   |-- requirements.txt
|   `-- test_main.py
|-- exercicio_9_3_render_hello_flask/
|   |-- app.py
|   |-- requirements.txt
|   `-- test_app.py
|-- exercicio_9_4_render_flask_restful/
|   |-- app.py
|   |-- requirements.txt
|   `-- test_app.py
|-- .github/workflows/
|   |-- ci.yml
|   |-- deploy-render.yml
|   `-- infra-validate-render.yml
|-- postman/
|   `-- Lab09_Render.postman_collection.json
|-- scripts/
|-- render.yaml
`-- README.md
```

## Entregaveis

1. Codigo-fonte dos exercicios:
   - `exercicio_9_1_flask`: API REST em Flask com CRUD de tarefas.
   - `exercicio_9_2_fastapi`: API REST em FastAPI com Swagger em `/docs`.
   - `exercicio_9_3_render_hello_flask`: Hello World Flask publicado no Render.
   - `exercicio_9_4_render_flask_restful`: API RESTful Flask publicada no Render.

2. Deploy no Render:
   - `render.yaml` com os quatro Web Services.
   - URLs publicadas na tabela "Links publicados".
   - Health checks em `/api/health`.

3. Testes automatizados:
   - Testes `pytest` em cada pasta de exercicio.
   - Workflow `.github/workflows/ci.yml` executando a matriz dos quatro projetos.

4. CI/CD e infraestrutura:
   - `.github/workflows/infra-validate-render.yml` valida o `render.yaml` pela API do Render.
   - `.github/workflows/deploy-render.yml` documenta o fluxo de deploy automatico pelo Render Blueprint.
   - `autoDeployTrigger: checksPass` configurado nos servicos do Render.

5. Postman:
   - Colecao: `postman/Lab09_Render.postman_collection.json`.
   - Variaveis ja configuradas com as URLs publicadas no Render.

6. Scripts auxiliares:
   - `scripts/test_local_all.sh`: instala dependencias e roda os testes locais.
   - `scripts/bootstrap_render_blueprint.sh`: prepara/valida o Blueprint no Render.
   - `scripts/status_render_blueprint.sh`: consulta status dos recursos no Render.

7. Prints recomendadas para anexar:
   - Quatro terminais locais rodando os exercicios 9.1, 9.2, 9.3 e 9.4.
   - Paginas/JSON das quatro URLs publicadas.
   - `/docs` do FastAPI no exercicio 9.2.
   - Resultado dos endpoints no Postman.
   - Aba Actions do GitHub com o workflow de CI.
   - Dashboard do Render mostrando os quatro servicos ativos.

## Como rodar localmente

Use quatro terminais separados.

Para abrir os quatro terminais automaticamente no Windows:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start_local_terminals.ps1
```

### Terminal 1 - Exercicio 9.1

```powershell
cd exercicio_9_1_flask
python -m pip install -r requirements.txt
$env:PORT = "5101"
python app.py
```

URL local: http://127.0.0.1:5101

### Terminal 2 - Exercicio 9.2

```powershell
cd exercicio_9_2_fastapi
python -m pip install -r requirements.txt
$env:PORT = "5102"
python main.py
```

URL local: http://127.0.0.1:5102  
Swagger: http://127.0.0.1:5102/docs

### Terminal 3 - Exercicio 9.3

```powershell
cd exercicio_9_3_render_hello_flask
python -m pip install -r requirements.txt
$env:PORT = "5103"
python app.py
```

URL local: http://127.0.0.1:5103

### Terminal 4 - Exercicio 9.4

```powershell
cd exercicio_9_4_render_flask_restful
python -m pip install -r requirements.txt
$env:PORT = "5104"
python app.py
```

URL local: http://127.0.0.1:5104

## Testes locais

Para rodar todos os testes:

```bash
./scripts/test_local_all.sh
```

Ou por pasta:

```powershell
cd exercicio_9_1_flask
python -m pip install -r requirements.txt
pytest -q
```

Repita o mesmo padrao para os demais exercicios.

## Deploy

O deploy foi feito pelo Render usando o arquivo `render.yaml`. Cada servico usa plano gratuito, health check em `/api/health` e deploy automatico quando os checks do GitHub passam.

Fluxo inicial do Blueprint:

```text
Render Dashboard > New + > Blueprint > selecionar repositorio > render.yaml > Deploy Blueprint
```

Depois da criacao inicial, novos pushes na branch principal disparam o fluxo de CI/CD.

## Status do Render

Depois de configurar `RENDER_API_KEY` e `RENDER_OWNER_ID`, consulte o status com:

```bash
./scripts/status_render_blueprint.sh
```

O script salva os retornos em:

```text
.render/render_blueprints_last.json
.render/render_services_last.json
.render/render_resources.env
```
