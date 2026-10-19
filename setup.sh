#!/usr/bin/env bash
#
# Configura e sobe o ambiente Docker do pipeline.
#
# Uso:
#   ./setup.sh            # build + up
#   ./setup.sh --run-now  # build + up + executa o pipeline agora
#
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v docker >/dev/null 2>&1; then
    echo "docker nao encontrado no PATH" >&2
    exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
    echo "docker compose (plugin v2) nao encontrado" >&2
    exit 1
fi

mkdir -p \
    data/bugcrowd \
    data/hackerone \
    data/processed \
    data/h1_processed \
    data/snapshots \
    data/scopes \
    data/logs

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Criado .env a partir de .env.example."
    echo "Preencha HACKERONE_USERNAME, HACKERONE_TOKEN e DISCORD_WEBHOOK antes de rodar."
fi

if grep -Eq '^(HACKERONE_USERNAME|HACKERONE_TOKEN|DISCORD_WEBHOOK)=$' .env; then
    echo "AVISO: ha variaveis vazias no .env; o HackerOne/notify pode falhar."
fi

docker compose build
docker compose up -d

echo -n "Aguardando o Scrapyd"
ready=0
for _ in $(seq 1 90); do
    if docker compose exec -T bbscraper \
        curl -fsS http://127.0.0.1:6800/daemonstatus.json >/dev/null 2>&1; then
        ready=1
        break
    fi
    echo -n "."
    sleep 2
done
echo

if [ "$ready" -ne 1 ]; then
    echo "Scrapyd nao respondeu. Ultimos logs:" >&2
    docker compose logs --tail=100 bbscraper >&2 || true
    exit 1
fi

echo "Ambiente pronto."
echo "  Scrapyd:        http://127.0.0.1:6800"
echo "  Dados no host:  $(pwd)/data"
echo "  Wildcards:      $(pwd)/data/scopes/all_scope_wildcards.txt"
echo "  Log pipeline:   $(pwd)/data/logs/pipeline.log"

if [ "${1:-}" = "--run-now" ]; then
    echo "Executando o pipeline agora (H1_DELAY_HOURS=${H1_DELAY_HOURS:-3})..."
    docker compose exec -T -e H1_DELAY_HOURS="${H1_DELAY_HOURS:-3}" \
        bbscraper /opt/scripts/run_pipeline.sh
fi
