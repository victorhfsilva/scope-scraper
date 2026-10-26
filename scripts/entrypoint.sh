#!/usr/bin/env bash
set -Eeuo pipefail

log() { printf '[entrypoint] %s %s\n' "$(date -Is)" "$*"; }

OUTPUT_ROOT="/output"
SCRAPYD_URL="${SCRAPYD_URL:-http://127.0.0.1:6800}"

mkdir -p \
    "$OUTPUT_ROOT/bugcrowd" \
    "$OUTPUT_ROOT/hackerone" \
    "$OUTPUT_ROOT/processed" \
    "$OUTPUT_ROOT/h1_processed" \
    "$OUTPUT_ROOT/snapshots" \
    "$OUTPUT_ROOT/scopes" \
    "$OUTPUT_ROOT/logs" \
    /var/log/scrapyd
chmod -R 0775 "$OUTPUT_ROOT" 2>/dev/null || true
# Mantem os arquivos acessiveis/gravaveis pelo usuario do host (bind mount ./data).
if [ -n "${PUID:-}" ] && [ -n "${PGID:-}" ]; then
    chown -R "${PUID}:${PGID}" "$OUTPUT_ROOT" 2>/dev/null || true
fi

if [ -n "${TZ:-}" ] && [ -f "/usr/share/zoneinfo/${TZ}" ]; then
    ln -snf "/usr/share/zoneinfo/${TZ}" /etc/localtime
    printf '%s\n' "$TZ" > /etc/timezone
    log "timezone definido para ${TZ}"
fi

# ----------------------------------------------------------------------
# Variaveis que o cron precisa receber (cron nao herda o ambiente do PID 1)
# Formato ${VAR:-valor}: permite sobrescrever em testes com `docker compose exec -e`.
# ----------------------------------------------------------------------
write_env_var() {
    local name="$1"
    local value="${!name-}"
    printf 'export %s=${%s:-%q}\n' "$name" "$name" "$value"
}

{
    for var in \
        SCRAPYD_URL \
        BUGCROWD_OUTPUT_DIR \
        HACKERONE_OUTPUT_DIR \
        H1_DELAY_HOURS \
        H1_DELAY_SECONDS \
        JOB_TIMEOUT_SECONDS \
        TZ \
        DISCORD_WEBHOOK \
        HACKERONE_USERNAME \
        HACKERONE_TOKEN \
        BUGCROWD_PROXY_LIST \
        HACKERONE_PROXY_LIST \
        PUID \
        PGID
    do
        write_env_var "$var"
    done
} > /opt/scripts/pipeline.env
chmod 0600 /opt/scripts/pipeline.env

# ----------------------------------------------------------------------
# notify: provider Discord a partir de DISCORD_WEBHOOK
# ----------------------------------------------------------------------
if [ -n "${DISCORD_WEBHOOK:-}" ]; then
    mkdir -p /root/.config/notify
    cat > /root/.config/notify/provider-config.yaml <<EOF
discord:
  - id: "discord"
    discord_channel: "bugbounty"
    discord_username: "notify"
    discord_format: "{{data}}"
    discord_webhook_url: "${DISCORD_WEBHOOK}"
EOF
    chmod 0600 /root/.config/notify/provider-config.yaml
    log "notify configurado para Discord"
else
    log "DISCORD_WEBHOOK vazio: notificacoes ficarao apenas no log"
fi

# ----------------------------------------------------------------------
# Scrapyd
# ----------------------------------------------------------------------
log "iniciando scrapyd"
scrapyd >"$OUTPUT_ROOT/logs/scrapyd.log" 2>&1 &
SCRAPYD_PID=$!

cleanup() {
    if [ -n "${SCRAPYD_PID:-}" ] && kill -0 "$SCRAPYD_PID" 2>/dev/null; then
        kill "$SCRAPYD_PID" 2>/dev/null || true
    fi
}
trap cleanup TERM INT EXIT

ready=0
for _ in $(seq 1 90); do
    if curl -fsS "${SCRAPYD_URL}/daemonstatus.json" >/dev/null 2>&1; then
        ready=1
        break
    fi
    if ! kill -0 "$SCRAPYD_PID" 2>/dev/null; then
        log "scrapyd encerrou durante a inicializacao"
        tail -n 100 "$OUTPUT_ROOT/logs/scrapyd.log" >&2 || true
        exit 1
    fi
    sleep 2
done
if [ "$ready" -ne 1 ]; then
    log "scrapyd nao respondeu em ${SCRAPYD_URL}"
    tail -n 100 "$OUTPUT_ROOT/logs/scrapyd.log" >&2 || true
    exit 1
fi
log "scrapyd pronto em ${SCRAPYD_URL}"

deploy_project() {
    local dir="$1"
    local name="$2"
    local attempt version
    for attempt in 1 2 3; do
        version="$(date +%Y%m%d%H%M%S)-${attempt}"
        log "deploy ${name} (tentativa ${attempt}, versao ${version})"
        if (cd "$dir" && scrapyd-deploy default --version "$version"); then
            return 0
        fi
        sleep 5
    done
    return 1
}

deploy_project /opt/BugcrowdScraper bugcrowdscraper || {
    log "falha ao publicar o projeto bugcrowdscraper"
    exit 1
}
deploy_project /opt/HackerOneScraper hackeronescraper || {
    log "falha ao publicar o projeto hackeronescraper"
    exit 1
}

# ----------------------------------------------------------------------
# Tarefa agendada
# ----------------------------------------------------------------------
CRON_SCHEDULE="${PIPELINE_CRON:-0 2 * * *}"
read -r _c1 _c2 _c3 _c4 _c5 _extra <<<"$CRON_SCHEDULE" || true
if [ -z "${_c5:-}" ] || [ -n "${_extra:-}" ]; then
    log "PIPELINE_CRON invalido: '${CRON_SCHEDULE}' (esperado: 'min hora dia mes dia-semana')"
    exit 1
fi

cat > /etc/cron.d/bbscraper <<EOF
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
HOME=/root
TZ=${TZ:-UTC}
${CRON_SCHEDULE} root /usr/bin/flock -n /tmp/bbscraper.lock /opt/scripts/run_pipeline.sh >> /output/logs/pipeline.log 2>&1
EOF
chmod 0644 /etc/cron.d/bbscraper

log "iniciando cron (agenda: ${CRON_SCHEDULE})"
cron

log "pipeline pronto"
wait "$SCRAPYD_PID"
