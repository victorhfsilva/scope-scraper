# Pipeline de scraping de escopos (Docker)

Automatiza a coleta de escopos publicos de Bugcrowd e HackerOne, o processamento
dos CSVs, a notificacao de diferencas no Discord e a geracao de uma lista
consolidada de dominios com wildcard.

## Arquitetura

Um unico container (`bugbounty-scraper`) roda:

- **Scrapyd** em `127.0.0.1:6800` (dentro do container) com dois projetos:
  - `bugcrowdscraper` / spider `engagementspider`
  - `hackeronescraper` / spider `scopesspider`
- **cron** com o pipeline diario
- **notify** (ProjectDiscovery) configurado para Discord
- as **venvs** de `BugcrowdCsvGrabber` e `HackerOneCsvGrabber`

O diretorio `./data` do host e montado em `/output` no container.

## Fluxo agendado

A cada execucao do cron (`PIPELINE_CRON`, padrao `0 2 * * *`):

1. agenda `bugcrowdscraper/engagementspider` no Scrapyd e espera terminar;
2. espera `H1_DELAY_HOURS` (padrao **3 horas**);
3. agenda `hackeronescraper/scopesspider` no Scrapyd e espera terminar;
4. processa os CSVs:
   - `/output/bugcrowd` -> `/output/processed`
   - `/output/hackerone` -> `/output/h1_processed`
5. gera:
   - `/output/scopes/all_scope_wildcards.txt` (`*.example.com`)
   - `/output/scopes/all_scope_domains.txt` (sem wildcard)
6. publica snapshots datados em `/output/snapshots`;
7. executa `notify_diff.sh /output/snapshots`, enviando ao Discord somente o
   que mudou entre a coleta atual e a anterior.

O `flock` impede que duas execucoes do pipeline se sobreponham.

## Configuracao

```bash
cp .env.example .env
```

Edite `.env`:

| Variavel | Descricao |
| --- | --- |
| `HACKERONE_USERNAME` / `HACKERONE_TOKEN` | credenciais da API do HackerOne |
| `DISCORD_WEBHOOK` | URL do webhook do Discord |
| `H1_DELAY_HOURS` | horas entre o fim do Bugcrowd e o inicio do HackerOne |
| `JOB_TIMEOUT_SECONDS` | timeout de cada crawl (padrao 21600 = 6h) |
| `PIPELINE_CRON` | agenda cron, no horario de `TZ` |
| `TZ` | timezone do container/cron |
| `PUID` / `PGID` | dono dos arquivos criados em `./data` |

O webhook do Discord e escrito em
`/root/.config/notify/provider-config.yaml` no inicio do container. Se trocar a
variavel, recrie o container:

```bash
docker compose up -d --force-recreate
```

## Subir o ambiente

```bash
./setup.sh
```

O script:

- cria `./data/{bugcrowd,hackerone,processed,h1_processed,snapshots,scopes,logs}`;
- cria `.env` a partir de `.env.example`, se ainda nao existir;
- faz o build da imagem;
- sobe o container;
- aguarda o Scrapyd;
- mostra os caminhos dos arquivos no host.

Para executar o pipeline imediatamente (em foreground):

```bash
./setup.sh --run-now
```

Para testar sem esperar 3 horas, use um atraso curto:

```bash
H1_DELAY_HOURS=0 ./setup.sh --run-now
```

## Acesso externo ao arquivo de dominios

O arquivo fica no bind mount, portanto e acessivel diretamente no host:

```bash
data/scopes/all_scope_wildcards.txt
```

Exemplo de conteudo:

```
*.api.example.com
*.example.com
*.sub.example.com
```

## Comandos manuais

```bash
# agendar somente o Bugcrowd
curl -s http://127.0.0.1:6800/schedule.json \
  -d project=bugcrowdscraper -d spider=engagementspider

# agendar somente o HackerOne
curl -s http://127.0.0.1:6800/schedule.json \
  -d project=hackeronescraper -d spider=scopesspider

# acompanhar jobs
curl -s "http://127.0.0.1:6800/listjobs.json?project=bugcrowdscraper" | jq

# rodar o pipeline completo manualmente
docker compose exec -T bbscraper /opt/scripts/run_pipeline.sh

# ver logs
tail -f data/logs/pipeline.log
tail -f data/logs/scrapyd.log
```

## Observacoes

- O Scrapyd e publicado apenas em `127.0.0.1:6800` do host.
- A API do HackerOne exige as credenciais; sem elas o spider falha e o
  processamento do HackerOne e ignorado, mas o restante do pipeline continua.
- Use o pipeline somente contra programas/escopos em que voce tem autorizacao
  para testar. O scraping aqui apenas coleta escopos publicos/credenciados.
- O `notify_diff.sh` precisa de pelo menos dois snapshots da mesma categoria
  para comparar; na primeira execucao ele apenas registra o snapshot inicial.
