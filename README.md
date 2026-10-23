# Bug Bounty Scraping

Pipeline em Docker para coletar, processar e monitorar os escopos públicos de
programas de bug bounty do **Bugcrowd** e do **HackerOne**.

O projeto automatiza todo o ciclo:

1. coleta os escopos no Bugcrowd;
2. aguarda algumas horas e coleta os escopos no HackerOne;
3. processa os CSVs exportados por cada plataforma;
4. compara os resultados com a coleta anterior;
5. notifica as mudanças no Discord;
6. gera uma lista consolidada de domínios no formato `*.example.com`.

> Use este projeto somente para consultar programas e escopos para os quais você
> tem autorização. Ele não realiza testes de intrusão nem acessa os alvos.

---

## Sumário

- [Como funciona](#como-funciona)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Configuração](#configuração)
- [Como utilizar](#como-utilizar)
- [Agendamento](#agendamento)
- [Arquivos gerados](#arquivos-gerados)
- [Notificações no Discord](#notificações-no-discord)
- [Comandos manuais](#comandos-manuais)
- [Logs e diagnóstico](#logs-e-diagnóstico)
- [Personalização](#personalização)
- [Segurança e escopo](#segurança-e-escopo)

---

## Como funciona

Tudo roda em um único container (`bugbounty-scraper`):

```
┌─────────────────────────────────────────────────────────────┐
│ container bugbounty-scraper                                 │
│                                                             │
│  cron ──► run_pipeline.sh                                   │
│              │                                              │
│              ├─► Scrapyd :6800                              │
│              │     ├─ bugcrowdscraper/engagementspider      │
│              │     └─ hackeronescraper/scopesspider         │
│              │                                              │
│              ├─► BugcrowdCsvGrabber  (venv)                 │
│              ├─► HackerOneCsvGrabber (venv)                 │
│              ├─► aggregate_wildcards.py                     │
│              ├─► notify_diff.sh ──► notify ──► Discord      │
│              └─► /output (bind mount ./data)                │
└─────────────────────────────────────────────────────────────┘
```

O diretório `./data` do host é montado em `/output` no container. Por isso todos
os resultados ficam acessíveis diretamente no host, inclusive o arquivo final de
domínios com wildcard.

O pipeline é executado diariamente pelo cron e protegido por `flock`, evitando
duas execuções simultâneas.

---

## Estrutura do projeto

```
.
├── Dockerfile
├── docker-compose.yml
├── setup.sh
├── .env.example
├── scripts/
│   ├── entrypoint.sh          # configura notify/cron, sobe o Scrapyd e publica os projetos
│   ├── run_pipeline.sh        # orquestra todo o fluxo
│   ├── aggregate_wildcards.py # consolida os domínios e adiciona "*."
│   └── publish_snapshots.sh   # organiza snapshots datados para o diff
├── notify_diff.sh             # compara snapshots e notifica mudanças
├── bugcrowdscraper/           # projeto Scrapy do Bugcrowd
├── HackerOneScraper/          # projeto Scrapy do HackerOne
├── BugcrowdCSVGrabber/        # processa CSV do Bugcrowd
├── HackerOneCsvGrabber/       # processa CSV do HackerOne
└── data/                      # criado em tempo de execução (volume do host)
```

---

## Pré-requisitos

- Docker Engine
- Docker Compose v2 (plugin `docker compose`)
- Credenciais da API do HackerOne
- Webhook do Discord (opcional, mas necessário para notificações)

Verifique:

```bash
docker --version
docker compose version
```

---

## Configuração

Crie o arquivo `.env`:

```bash
cp .env.example .env
```

Edite `.env`:

| Variável | Obrigatória | Descrição |
|---|---:|---|
| `HACKERONE_USERNAME` | Sim | Usuário da API do HackerOne |
| `HACKERONE_TOKEN` | Sim | Token da API do HackerOne |
| `DISCORD_WEBHOOK` | Recomendada | URL do webhook do Discord |
| `H1_DELAY_HOURS` | Não | Horas entre o fim do Bugcrowd e o início do HackerOne. Padrão: `3` |
| `JOB_TIMEOUT_SECONDS` | Não | Timeout de cada crawl. Padrão: `21600` (6h) |
| `PIPELINE_CRON` | Não | Agenda cron. Padrão: `0 2 * * *` (diariamente às 02:00) |
| `TZ` | Não | Timezone do container/cron. Padrão: `America/Sao_Paulo` |
| `PUID` / `PGID` | Não | UID/GID do host que será dono dos arquivos em `./data`. Padrão: `1000` |

As credenciais do HackerOne podem ser obtidas em:

```text
https://hackerone.com/settings/api_token
```

Para criar um webhook no Discord:

```text
Configurações do canal → Integrações → Webhooks → Novo webhook → Copiar URL
```

---

## Como utilizar

### 1. Subir o ambiente

```bash
./setup.sh
```

O script:

- cria `./data/{bugcrowd,hackerone,processed,h1_processed,snapshots,scopes,logs}`;
- cria `.env` a partir de `.env.example`, se necessário;
- faz o build da imagem;
- sobe o container;
- aguarda o Scrapyd ficar disponível;
- mostra os caminhos dos arquivos no host.

### 2. Executar imediatamente

Para rodar o pipeline agora, sem esperar o cron:

```bash
./setup.sh --run-now
```

Para um teste rápido, sem esperar 3 horas:

```bash
H1_DELAY_HOURS=0 ./setup.sh --run-now
```

Também é possível rodar diretamente:

```bash
docker compose exec -T bbscraper /opt/scripts/run_pipeline.sh
```

### 3. Acompanhar

```bash
docker compose ps
docker compose logs -f bbscraper
tail -f data/logs/pipeline.log
tail -f data/logs/scrapyd.log
```

### 4. Parar ou remover

```bash
docker compose stop
docker compose down
```

Os dados em `./data` são preservados.

---

## Agendamento

Por padrão, o cron executa o pipeline diariamente às 02:00 no timezone
configurado em `TZ`:

```cron
0 2 * * * root /usr/bin/flock -n /tmp/bbscraper.lock \
  /opt/scripts/run_pipeline.sh >> /output/logs/pipeline.log 2>&1
```

Sequência executada:

1. agenda `bugcrowdscraper/engagementspider` no Scrapyd;
2. espera o job finalizar (ou atingir `JOB_TIMEOUT_SECONDS`);
3. aguarda `H1_DELAY_HOURS`;
4. agenda `hackeronescraper/scopesspider`;
5. espera o job finalizar;
6. processa os CSVs;
7. gera a lista consolidada de domínios;
8. publica snapshots datados;
9. executa o `notify_diff.sh`.

Para mudar o horário, edite `PIPELINE_CRON` no `.env` e recrie o container:

```bash
docker compose up -d --force-recreate
```

O formato é o cron padrão:

```text
minuto hora dia-do-mês mês dia-da-semana
```

---

## Arquivos gerados

### Domínios consolidados

Este é o arquivo procurado para usar em outras ferramentas:

```text
./data/scopes/all_scope_wildcards.txt
```

Conteúdo de exemplo:

```text
*.api.example.com
*.example.com
*.sub.example.com
```

Também é gerada a versão sem `*.`:

```text
./data/scopes/all_scope_domains.txt
```

### Domínios novos (diff)

A cada execução o pipeline compara o escopo consolidado atual com o da execução
anterior e grava apenas os domínios/wildcards que **não** estavam no escopo
antigo:

```text
./data/scopes/all_scope_domains_new.txt     # exemplo.com (sem wildcard)
./data/scopes/all_scope_wildcards_new.txt   # *.example.com
```

Se não houver arquivo anterior (primeira execução), todos os domínios são
considerados novos.

### CSVs brutos

```text
./data/bugcrowd/YYYY-MM-DD-scopes.csv
./data/hackerone/YYYY-MM-DD-scopes.csv
```

### Resultados processados

```text
./data/processed/YYYYMMDD_cleaned_domains.txt
./data/processed/YYYYMMDD_cleaned_ips.txt
./data/processed/YYYYMMDD_rough_websites.txt
./data/processed/YYYYMMDD_rough_apis.txt
...

./data/h1_processed/YYYYMMDD_cleaned_urls.txt
./data/h1_processed/YYYYMMDD_wildcards_domains.txt
./data/h1_processed/YYYYMMDD_expanded_ip_addresses.txt
...
```

### Snapshots para comparação

```text
./data/snapshots/YYYYMMDD_bugcrowd_cleaned_domains.txt
./data/snapshots/YYYYMMDD_hackerone_cleaned_urls.txt
./data/snapshots/YYYYMMDD_all_scope_wildcards.txt
...
```

O `notify_diff.sh` compara o snapshot mais recente com o anterior de cada
categoria. Na primeira execução não há histórico, então ele apenas registra a
base inicial.

### Logs

```text
./data/logs/pipeline.log
./data/logs/scrapyd.log
```

---

## Notificações no Discord

O binário `notify` (ProjectDiscovery) é instalado na imagem. No início do
container, a partir de `DISCORD_WEBHOOK`, ele gera:

```text
/root/.config/notify/provider-config.yaml
```

O `notify_diff.sh` envia:

- um resumo por categoria com itens novos e removidos;
- um resumo geral da execução.

Se `DISCORD_WEBHOOK` estiver vazio, o pipeline continua normalmente e as
notificações são apenas registradas no log (`--no-notify`).

Após alterar o webhook, recrie o container:

```bash
docker compose up -d --force-recreate
```

Para testar o notify manualmente:

```bash
docker compose exec -T bbscraper sh -c \
  'printf "teste notify\n" | notify -disable-update-check'
```

---

## Comandos manuais

### Scrapyd

```bash
# status
curl -s http://127.0.0.1:6800/daemonstatus.json | jq

# projetos publicados
curl -s http://127.0.0.1:6800/listprojects.json | jq

# spiders de cada projeto
curl -s "http://127.0.0.1:6800/listspiders.json?project=bugcrowdscraper" | jq
curl -s "http://127.0.0.1:6800/listspiders.json?project=hackeronescraper" | jq
```

### Agendar um spider específico

```bash
# Bugcrowd
curl -s http://127.0.0.1:6800/schedule.json \
  -d project=bugcrowdscraper \
  -d spider=engagementspider

# HackerOne
curl -s http://127.0.0.1:6800/schedule.json \
  -d project=hackeronescraper \
  -d spider=scopesspider
```

### Acompanhar jobs

```bash
curl -s "http://127.0.0.1:6800/listjobs.json?project=bugcrowdscraper" | jq
curl -s "http://127.0.0.1:6800/listjobs.json?project=hackeronescraper" | jq
```

### Processar CSVs manualmente

```bash
docker compose exec -T bbscraper \
  /opt/BugcrowdCsvGrabber/venv/bin/BugcrowdCsvGrabber \
  --input /output/bugcrowd \
  --output /output/processed

docker compose exec -T bbscraper \
  /opt/HackerOneCsvGrabber/venv/bin/HackerOneCsvGrabber \
  --input /output/hackerone \
  --output /output/h1_processed
```

### Gerar a lista de wildcards manualmente

```bash
docker compose exec -T bbscraper python3 /opt/scripts/aggregate_wildcards.py \
  --output /output/scopes/all_scope_wildcards.txt \
  --plain-output /output/scopes/all_scope_domains.txt
```

### Rodar o diff manualmente

```bash
docker compose exec -T bbscraper /opt/scripts/notify_diff.sh /output/snapshots
```

Para visualizar sem enviar ao Discord:

```bash
docker compose exec -T bbscraper \
  /opt/scripts/notify_diff.sh /output/snapshots --no-notify
```

---

## Logs e diagnóstico

### Container não sobe

```bash
docker compose logs --tail=200 bbscraper
```

### Scrapyd não responde

```bash
curl -v http://127.0.0.1:6800/daemonstatus.json
docker compose exec -T bbscraper \
  curl -s http://127.0.0.1:6800/daemonstatus.json
```

### Ver o log de um job

O Scrapyd guarda os logs dos jobs em `/opt/logs` dentro do container:

```bash
docker compose exec -T bbscraper sh -c \
  'find /opt/logs -type f -name "*.log" | sort | tail'
```

### O HackerOne não gerou CSV

Verifique as credenciais no `.env` e recrie o container:

```bash
docker compose up -d --force-recreate
docker compose logs --tail=100 bbscraper
```

### Recomeçar do zero

```bash
docker compose down
rm -rf data
./setup.sh
```

> Atenção: isso apaga todo o histórico usado pelo `notify_diff.sh`.

---

## Personalização

### Horário do pipeline

Edite no `.env`:

```dotenv
PIPELINE_CRON=30 1 * * *
```

### Tempo entre Bugcrowd e HackerOne

```dotenv
H1_DELAY_HOURS=6
```

### Timeout dos crawls

```dotenv
JOB_TIMEOUT_SECONDS=43200
```

### Dados em outro diretório do host

Edite o bind mount no `docker-compose.yml`:

```yaml
volumes:
  - /caminho/desejado:/output
```

### Dono dos arquivos

```dotenv
PUID=1000
PGID=1000
```

Use os valores retornados por:

```bash
id -u
id -g
```

### Proxies

Os projetos Scrapy suportam proxies. Coloque a lista em:

```text
/opt/BugcrowdScraper/proxies.txt
/opt/HackerOneScraper/proxies.txt
```

Como esses arquivos ficam dentro da imagem, para persistir proxies próprios é
necessário adicionar volumes no `docker-compose.yml` ou rebuildar a imagem.

---

## Segurança e escopo

- O Scrapyd é publicado apenas em `127.0.0.1:6800` no host.
- As credenciais ficam no `.env` e em `/opt/scripts/pipeline.env` com permissão
  `0600` dentro do container.
- O projeto coleta apenas escopos públicos ou acessíveis com as credenciais
  fornecidas.
- Respeite os termos de uso das plataformas e os limites de taxa.
- Utilize os domínios coletados somente em programas nos quais você tem
  autorização explícita para atuar.
