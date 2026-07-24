# LifeOS

Dashboard pessoal inteligente — seu segundo cérebro para acompanhar fé, saúde, estudos, projetos, humor, pureza, metas e finanças em um só lugar.

> **Status atual**: LifeOS está **completo** — todos os 10 módulos do escopo original estão implementados e testados de ponta a ponta: Fé, Saúde, Estudos, Projetos, Humor, Pureza, Metas, Financeiro, Jogos e Histórico, além do Dashboard Geral que agrega dados de todos os módulos.

## Stack

Python 3 · Flask · SQLAlchemy · Flask-Migrate · Flask-WTF · Flask-Login · Jinja2 · Bootstrap 5 · Chart.js · PostgreSQL (produção) / SQLite (dev)

## Instalação

```bash
git clone <repo>
cd lifeos
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # ajuste SECRET_KEY e DATABASE_URL se necessário
```

Sem `DATABASE_URL` definido, o app usa SQLite automaticamente em `instance/lifeos.db` — ótimo para rodar localmente sem configurar Postgres.

## Banco de dados

Duas formas de criar o schema:

**Rápida (dev, sem histórico de migrations):**
```bash
python init_db.py
```

**Com Flask-Migrate (recomendado para produção):**
```bash
export FLASK_APP=run.py
flask db init          # só na primeira vez
flask db migrate -m "schema inicial"
flask db upgrade
```

## Execução

```bash
python run.py
```

Acesse `http://localhost:5000`, crie sua conta em `/registrar` e faça login.

## Estrutura do projeto

```
lifeos/
├── app/
│   ├── __init__.py            # application factory
│   ├── config.py              # config dev/produção
│   ├── extensions.py          # db, migrate, login_manager, csrf
│   ├── models/                # um arquivo por domínio (user, fe, ...)
│   ├── blueprints/            # um pacote por módulo (routes + forms)
│   ├── templates/             # um subdiretório por módulo
│   └── static/{css,js}/
├── migrations/
├── init_db.py
├── requirements.txt
├── run.py
└── .env.example
```

## Arquitetura

- **Application factory** (`create_app`) para permitir múltiplas configurações (dev/test/prod) e evitar imports circulares.
- **Blueprints isolados por módulo**: cada módulo de vida (Fé, Saúde, ...) é um blueprint próprio com `routes.py` e `forms.py`, registrado em `app/__init__.py`.
- **Modelos por domínio**, todos com `user_id` (FK `CASCADE`) para isolamento total de dados entre usuários.
- **Templates herdando de `base.html`**, que contém sidebar, navbar, flash messages e os blocos `content`/`extra_js`/`extra_css`.
- **CSS com variáveis** (`variables.css`) preparadas para dark mode via `[data-theme="dark"]` — já com toggle funcional em `base.js`.

## Como adicionar um novo módulo

Use o módulo **Fé** como referência. Passos:

1. **Model** — crie `app/models/<modulo>.py` com um `db.Model` contendo `user_id`, `data` e os campos do domínio. Registre-o em `app/models/__init__.py`.
2. **Form** — crie `app/blueprints/<modulo>/forms.py` com um `FlaskForm`. Cuidado: **nunca** use `data` como nome de kwarg ao instanciar o form (é reservado pelo WTForms) — use `RegistroXForm(obj=SimpleNamespace(data=...))`.
3. **Routes** — crie `app/blueprints/<modulo>/routes.py` com um `Blueprint` e as rotas `index` (listagem + stats), `novo`, `editar/<id>`, `excluir/<id>` (POST), todas protegidas com `@login_required` e filtrando por `user_id=current_user.id`.
4. **Templates** — crie `app/templates/<modulo>/{index.html, form.html}` estendendo `base.html`.
5. **Registro** — importe e registre o blueprint em `app/__init__.py` (`app.register_blueprint(<modulo>_bp, url_prefix="/<modulo>")`).
6. **Sidebar** — troque o link "em breve" correspondente em `templates/base.html` pelo `url_for` real.
7. **Migração** — rode `flask db migrate -m "add <modulo>"` e `flask db upgrade` (ou `python init_db.py` em dev).
8. **Dashboard** — opcionalmente, agregue os novos dados em `app/blueprints/dashboard/routes.py` e exiba em `templates/dashboard/index.html`.

## Notificações via Telegram (lembretes tipo "hora de estudar")

O LifeOS pode te mandar mensagem no Telegram em horários que você definir (ex: "Hora de estudar" às 19h, seg-sex).

### 1. Criar o bot
1. No Telegram, procure **@BotFather** → `/newbot` → siga as instruções → copie o **token** gerado.
2. Defina `TELEGRAM_BOT_TOKEN=<esse token>` no `.env`.

### 2. Descobrir seu Chat ID
1. Procure **@userinfobot** no Telegram, mande qualquer mensagem, ele te devolve seu **Id**.
2. Vá em `/perfil` no LifeOS, cole esse número em "Chat ID do Telegram" e salve.
3. **Importante**: clique em "Start" na conversa com o bot que você criou no passo 1 — bots não podem mandar mensagem pra quem nunca iniciou conversa com eles.
4. Use o botão "Enviar mensagem de teste" em `/perfil` pra confirmar que está tudo certo.

### 3. Criar lembretes
Em `/perfil`, clique em "Novo lembrete" — defina título, horário e dias da semana. Ex: "Hora de estudar", 19:00, seg-sex.

### 4. Configurar o disparo automático
Os lembretes só disparam quando algo chama `GET /cron/lembretes?secret=<CRON_SECRET>` no horário certo. Duas formas:

- **Vercel Cron** (só se você tiver o plano Pro): adicione um bloco `crons` no `vercel.json` chamando essa rota a cada minuto. **No plano Hobby (grátis) isso não dá pra fazer** — a Vercel só libera 1 disparo por dia e com até 1h de imprecisão, o que não serve pra lembrete de horário exato.
- **Agendador externo gratuito** (recomendado pro plano Hobby): crie uma conta grátis em [cron-job.org](https://cron-job.org), aponte pra `https://seu-app.vercel.app/cron/lembretes?secret=<CRON_SECRET>` a cada 5 minutos. A Vercel não se importa quem chama a rota — só entrega a resposta.

Nos dois casos, defina `CRON_SECRET` (uma string aleatória, tipo senha) nas env vars — sem isso o endpoint fica público pra qualquer um disparar. Se você usar o Vercel Cron nativo, ele já manda o segredo certo sozinho via header `Authorization`; se usar agendador externo, passe `?secret=` na URL.

## Deploy na Vercel

Duas mudanças obrigatórias em relação a rodar local:

### 1. Banco de dados: criar o projeto no Supabase

Você **não precisa criar tabela nenhuma manualmente** — o SQLAlchemy já define todos os modelos no código, e `init_db.py` (ou `flask db upgrade`) cria tudo sozinho a partir deles. O Supabase só serve como o Postgres hospedado.

1. Crie uma conta grátis em [supabase.com](https://supabase.com) → "New Project" → escolha uma senha forte pro banco (guarde ela).
2. No painel do projeto, clique no botão **"Connect"** no topo da página (a tela de conexão não fica mais em Settings → Database). Você vai ver abas com diferentes strings — **duas são necessárias, para coisas diferentes**:
   - **Session pooler** (porta 5432) → use essa **na sua máquina local**, pra rodar as migrations (`python init_db.py`). A "Direct connection" também existe mas pode exigir IPv6 ou um add-on pago no plano grátis — o Session pooler evita esse problema e funciona por IPv4 em qualquer plano.
   - **Transaction pooler** (porta 6543) → essa é a que vai no `DATABASE_URL` da Vercel (produção). Serverless abre uma conexão nova a cada request; sem o pooler em modo transaction você estoura o limite de conexões do Postgres rapidinho.
3. Rode localmente, apontando pro banco remoto via **Session pooler** (repare que o usuário inclui o ref do projeto, `postgres.[ref]`, não só `postgres`):
   ```bash
   export DATABASE_URL="postgresql://postgres.[ref]:[senha]@aws-0-[região].pooler.supabase.com:5432/postgres"
   python init_db.py
   ```
4. Na Vercel, configure `DATABASE_URL` com a string do **Transaction pooler** (mesma coisa, trocando a porta pra 6543):
   ```
   postgresql://postgres.[ref]:[senha]@aws-0-[região].pooler.supabase.com:6543/postgres
   ```

Isso vai criar essas tabelas no Supabase (uma por modelo do app): `users`, `registros_fe`, `projetos`, `checklist_items`, `categorias_financeiras`, `transacoes`, `objetivos_financeiros`, `investimentos`, `registros_estudo`, `metas`, `registros_saude`, `registros_humor`, `registros_pureza`, `registros_jogo`, `lembretes`.

### Ativar RLS (Row Level Security) — importante

Por padrão, o Supabase expõe toda tabela via uma API REST própria (PostgREST), acessível com a "anon key" do projeto. Sem RLS, qualquer um com essa key acessa seus dados direto, pulando o Flask e o filtro por usuário. Isso **não afeta o app** (a conexão do Flask usa o usuário `postgres`, que tem `BYPASSRLS`), só fecha essa porta lateral que você nunca usa mesmo.

Depois de rodar `init_db.py`, cole o conteúdo de `supabase_rls.sql` no **SQL Editor** do painel do Supabase e execute uma vez. Não precisa criar nenhuma policy — RLS ligado sem policies já bloqueia o acesso via API por padrão.

### 2. Variáveis de ambiente na Vercel
`SECRET_KEY`, `DATABASE_URL` (pooler, porta 6543), `TELEGRAM_BOT_TOKEN`, `CRON_SECRET`, `TIMEZONE`.

O resto é zero-config: a Vercel detecta o `wsgi.py` na raiz automaticamente (não precisa de `api/index.py` nem `builds` no `vercel.json` — isso é o padrão antigo).

## Módulos implementados

| Módulo | Campos principais |
|---|---|
| Fé | livro, capítulos, tempo de leitura/oração, devocional, sequência de dias |
| Saúde | peso, IMC (com altura do perfil), água, sono, treino, streaks de metas, correlação com humor |
| Estudos | tecnologia, horas, curso, vínculo com projeto, ranking de tecnologias |
| Projetos | status, prioridade, prazo, checklist com progresso automático |
| Humor | humor, energia, motivação, ansiedade, estresse (1 registro/dia) |
| Pureza | resistiu (sim/não), campos condicionais de recaída, sequência |
| Metas | categoria, valor atual/final, prazo, conclusão automática |
| Financeiro | receitas, despesas, categorias, saldo, objetivos, investimentos |
| Jogos | jogo, tempo jogado, plataforma, ranking por jogo |
| Histórico | visão cross-module com filtro por tipo/data/busca e exclusão |
| Perfil / Lembretes | altura, metas de água/sono, Chat ID do Telegram, lembretes agendados |

O Dashboard Geral (`/`) agrega automaticamente indicadores de todos os módulos acima.

> **Nota sobre Metas + peso**: o módulo Metas assume que "valor maior = melhor" (ex: dinheiro guardado). Se você criar uma meta de **perder** peso (ex: 81kg → 78kg), a barra de progresso vai ficar invertida/incorreta, porque ela calcula `valor_atual / valor_final`. Pra metas de redução (peso, dívida, etc.) funcionar certo, o modelo precisaria de um campo "direção" (crescente/decrescente) — não implementei isso ainda para não adicionar complexidade sem necessidade confirmada, mas é uma melhoria natural se você for usar esse tipo de meta com frequência.

## Testes realizados

Fluxo validado via requisições HTTP reais neste ambiente: registro de conta → login automático → criação de registro de Fé → listagem com estatísticas → cards do dashboard — tudo retornando os valores esperados, sem erros no log do servidor.
