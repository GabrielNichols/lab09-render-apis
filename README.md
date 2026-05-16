# Lab 09 — APIs e Microsserviços com Render Blueprint

Este projeto resolve os exercícios do Laboratório 9 usando **Flask**, **FastAPI**, **Postman**, **GitHub Actions** e **Render Free**.

A implantação em nuvem foi adaptada para **Render Blueprint**, usando o arquivo `render.yaml` na raiz do repositório.

## Estrutura

```text
.
├── exercicio_9_1_flask/
├── exercicio_9_2_fastapi/
├── exercicio_9_3_render_hello_flask/
├── exercicio_9_4_render_flask_restful/
├── .github/workflows/
├── postman/
├── scripts/
└── render.yaml
```

## Deploy correto no Render

O fluxo correto agora é:

1. Rodar o script de bootstrap.
2. O script valida o `render.yaml` na API do Render.
3. O script configura secrets no GitHub usando `gh secret set`.
4. O script faz commit/push para o GitHub.
5. Você cria o Blueprint uma única vez no Render Dashboard.
6. Depois disso, cada push na branch principal dispara CI/CD automaticamente.

## Comando principal

Na raiz do projeto:

```bash
chmod +x scripts/*.sh
./scripts/bootstrap_render_blueprint.sh
```

O comando antigo também funciona e redireciona para o novo fluxo:

```bash
./scripts/bootstrap_render_infra.sh
```

## Variáveis aceitas pelo script

Você pode informar no terminal quando o script pedir, ou exportar antes:

```bash
export RENDER_API_KEY="sua_api_key_do_render"
export RENDER_OWNER_ID="seu_workspace_id_do_render"
```

## O que o script mostra

O script agora é verboso e mostra:

- diretório do projeto;
- arquivo de log criado em `.render/`;
- checagem de `git`, `gh`, `curl` e `python3`;
- status de autenticação do GitHub CLI;
- lista de workspaces/owners encontrados no Render;
- validação do `render.yaml`;
- criação/atualização de secrets no GitHub;
- commit e push;
- instruções para criar o Blueprint no Render;
- tentativa de descobrir Blueprint e serviços criados.

## Por que ainda existe uma etapa manual no Render?

O Render Blueprint precisa ser conectado ao repositório pela primeira vez no Dashboard:

```text
Render Dashboard > New + > Blueprint > selecionar repositório > render.yaml > Deploy Blueprint
```

Depois dessa criação inicial, o Blueprint fica conectado ao repositório e o deploy passa a ser automático.

## CI/CD

### CI

Arquivo:

```text
.github/workflows/ci.yml
```

Roda os testes de todos os exercícios.

### Validação de infraestrutura

Arquivo:

```text
.github/workflows/infra-validate-render.yml
```

Valida o `render.yaml` pela API do Render.

### Deploy

O deploy é controlado pelo próprio Render Blueprint porque cada serviço no `render.yaml` usa:

```yaml
autoDeployTrigger: checksPass
```

Isso significa que o Render só faz deploy quando os checks do GitHub passam.

## Acompanhar status depois

Depois de criar o Blueprint no Render, rode:

```bash
./scripts/status_render_blueprint.sh
```

Ele consulta a API do Render e salva respostas completas em:

```text
.render/render_blueprints_last.json
.render/render_services_last.json
.render/render_resources.env
```

## Testes locais

```bash
./scripts/test_local_all.sh
```

## Postman

Importe a coleção:

```text
postman/Lab09_Render.postman_collection.json
```

Depois ajuste as variáveis conforme as URLs geradas pelo Render.
