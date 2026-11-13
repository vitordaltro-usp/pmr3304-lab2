# Giro Diário — Lab 2 de PMR3304

Site de notícias feito com Django para a segunda entrega de laboratório de
PMR3304 (Sistemas de Informação, Poli-USP). É uma aplicação CRUD com posts,
comentários e categorias.

## Funcionalidades

- Listagem de posts (`/`), do mais recente ao mais antigo, com link para cada post.
- Página do post (`/post/<id>/`): conteúdo em HTML, data, categorias e comentários.
- Criação, edição e remoção de posts pela própria aplicação (`/post/novo/`,
  `/post/<id>/editar/`, `/post/<id>/remover/`, com página de confirmação).
- Comentários (`/post/<id>/comentar/`): exigem login; o autor é o usuário logado.
- Categorias (`/categorias/` e `/categorias/<id>/`).
- Login e logout nativos do Django em `/contas/login/`; administração em `/admin/`.

As views de post foram escritas em três versões, cada uma em um commit:
funções sem forms, funções com Django form e classes genéricas.
Comentários e categorias foram desenvolvidos nos branches `comments` e
`categories`, mesclados no `main`.

## Como rodar localmente (Windows)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata seed_data.json
python manage.py createsuperuser
python manage.py runserver
```

Acesse http://127.0.0.1:8000/. Para comentar, faça login com um usuário criado
pelo admin. Os usuários da fixture (marina, carlos, ana, pedro) servem só
como autores dos comentários de exemplo e não têm senha utilizável.

Testes automáticos:

```bash
python manage.py test blog
```

## Variáveis de ambiente

| Variável | Padrão (desenvolvimento) | Produção |
|---|---|---|
| `SECRET_KEY` | chave insegura de desenvolvimento | obrigatória (a aplicação não sobe sem ela quando `DEBUG=False`) |
| `DEBUG` | `True` | `False` |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,.onrender.com` | o padrão já serve para o Render |
| `CSRF_TRUSTED_ORIGINS` | `https://*.onrender.com` | o padrão já serve para o Render |

## Deploy no Render

1. Crie um **Web Service** a partir do repositório no GitHub.
2. Configure:
   - **Runtime:** Python 3
   - **Build command:**
     `pip install -r requirements.txt && python manage.py migrate && python manage.py loaddata seed_data.json`
   - **Start command:** `gunicorn config.wsgi`
3. Em **Environment**, defina:
   - `SECRET_KEY`: um valor longo e aleatório (o Render tem um botão "Generate");
   - `DEBUG`: `False`;
   - `PYTHON_VERSION`: `3.12.10`.

Para ter um administrador em produção (opcional), defina também
`DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL` e
`DJANGO_SUPERUSER_PASSWORD` nas variáveis do Render e acrescente ao fim do
build command:
`&& (python manage.py createsuperuser --noinput || true)`.

### Limitações conhecidas

- O disco do plano gratuito do Render não é persistente: posts e comentários
  criados no site em produção podem ser perdidos a cada novo deploy ou
  reinício. A cada build, a fixture recria os dados de exemplo.
- O `db.sqlite3` entregue no Moodle é o **local**, não o do Render.
- O CSS do site está inline em `templates/base.html`, então as páginas do site
  aparecem com estilo. O admin, porém, aparece sem estilo em produção, porque
  o projeto não usa pacotes extras (como o `whitenoise`) para servir arquivos
  estáticos.

## Estrutura

```
config/            projeto Django (settings, urls, wsgi)
blog/              app: models, views, urls, forms, admin, tests
blog/fixtures/     seed_data.json com os dados de exemplo
templates/         base.html, blog/ e registration/
queries.sql        as 5 consultas SQL da seção 4 do enunciado
```
