-- Ativa Row Level Security em todas as tabelas do LifeOS.
--
-- Por quê: o Supabase expõe toda tabela automaticamente via API REST
-- (PostgREST) usando a "anon key" do projeto. Sem RLS, qualquer um com essa
-- key consegue ler/escrever direto no banco, ignorando o filtro por usuário
-- que o Flask faz em cada rota.
--
-- Isso NÃO afeta o funcionamento do LifeOS: a conexão do Flask usa o usuário
-- `postgres` (dono do banco), que tem BYPASSRLS por padrão — RLS só passa a
-- bloquear o acesso via a API REST do Supabase, que o app não usa.
--
-- Não é necessário criar nenhuma policy: RLS ligado sem policies = acesso
-- negado por padrão via API, e sem nenhum efeito na conexão direta do Flask.
--
-- Como rodar: cole isso no SQL Editor do Supabase (painel do projeto) e
-- execute uma vez, depois de rodar o init_db.py.

ALTER TABLE users                    ENABLE ROW LEVEL SECURITY;
ALTER TABLE registros_fe             ENABLE ROW LEVEL SECURITY;
ALTER TABLE projetos                 ENABLE ROW LEVEL SECURITY;
ALTER TABLE checklist_items          ENABLE ROW LEVEL SECURITY;
ALTER TABLE categorias_financeiras   ENABLE ROW LEVEL SECURITY;
ALTER TABLE transacoes               ENABLE ROW LEVEL SECURITY;
ALTER TABLE objetivos_financeiros    ENABLE ROW LEVEL SECURITY;
ALTER TABLE investimentos            ENABLE ROW LEVEL SECURITY;
ALTER TABLE registros_estudo         ENABLE ROW LEVEL SECURITY;
ALTER TABLE metas                    ENABLE ROW LEVEL SECURITY;
ALTER TABLE registros_saude          ENABLE ROW LEVEL SECURITY;
ALTER TABLE registros_humor          ENABLE ROW LEVEL SECURITY;
ALTER TABLE registros_pureza         ENABLE ROW LEVEL SECURITY;
ALTER TABLE registros_jogo           ENABLE ROW LEVEL SECURITY;
ALTER TABLE lembretes                ENABLE ROW LEVEL SECURITY;
