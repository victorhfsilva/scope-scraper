#!/usr/bin/env bash
#
# Orquestra o pipeline completo:
#   1. Bugcrowd (engagementspider)
#   2. espera H1_DELAY_HOURS
#   3. HackerOne (scopesspider)
#   4. processa os CSV dos dois
#   5. gera a lista de dominios com wildcard
#   6. publica snapshots e roda o notify_diff.sh
#
set -uo pipefail

export HOME="${HOME:-/root}"

if [ -f /opt/scripts/pipeline.env ]; then
    # shellcheck disable=SC1091
    . /opt/scripts/pipeline.env
fi

SCRAPYD_URL="${SCRAPYD_URL:-http://127.0.0.1:6800}"
JOB_TIMEOUT_SECONDS="${JOB_TIMEOUT_SECONDS:-21600}"
H1_DELAY_HOURS="${H1_DELAY_HOURS:-3}"

log() { printf '[pipeline] %s %s\n' "$(date -Is)" "$*" >&2; }

notify_msg() {
    local msg="$1"
    if [ -n "${DISCORD_WEBHOOK:-}" ] && command -v notify >/dev/null 2>&1; then
        printf '%s\n' "$msg" | notify -silent -disable-update-check >/dev/null 2>&1 || true
    fi
}

schedule_spider() {
    local project="$1"
    local spider="$2"
    local resp status jobid

    resp="$(curl -fsS -X POST "${SCRAPYD_URL}/schedule.json" \
        --data-urlencode "project=${project}" \
        --data-urlencode "spider=${spider}" 2>/dev/null)" || {
        log "erro ao agendar ${project}/${spider} em ${SCRAPYD_URL}"
        return 1
    }

    status="$(printf '%s' "$resp" | jq -r '.status // "error"')"
    jobid="$(printf '%s' "$resp" | jq -r '.jobid // empty')"

    if [ "$status" != "ok" ] || [ -z "$jobid" ]; then
        log "agendamento recusado para ${project}/${spider}: ${resp}"
        return 1
    fi

    log "job agendado: project=${project} spider=${spider} jobid=${jobid}"
    printf '%s\n' "$jobid"
}

wait_for_job() {
    local project="$1"
    local jobid="$2"
    local timeout="${3:-$JOB_TIMEOUT_SECONDS}"
    local start now elapsed json state

    start="$(date +%s)"
    while :; do
        now="$(date +%s)"
        elapsed=$((now - start))
        if [ "$elapsed" -ge "$timeout" ]; then
            log "timeout (${timeout}s) aguardando job ${jobid}; cancelando"
            curl -fsS -X POST "${SCRAPYD_URL}/cancel.json" \
                --data-urlencode "project=${project}" \
                --data-urlencode "job=${jobid}" >/dev/null 2>&1 || true
            return 1
        fi

        if ! json="$(curl -fsS "${SCRAPYD_URL}/listjobs.json?project=${project}" 2>/dev/null)"; then
            log "scrapyd indisponivel; nova tentativa em 15s"
            sleep 15
            continue
        fi

        state="$(printf '%s' "$json" | jq -r --arg id "$jobid" '
            if any(.pending[]?; .id == $id) then "pending"
            elif any(.running[]?; .id == $id) then "running"
            elif any(.finished[]?; .id == $id) then "finished"
            else "" end')"

        case "$state" in
            finished)
                log "job ${jobid} finalizado apos ${elapsed}s"
                return 0
                ;;
            pending|running)
                sleep 20
                ;;
            "")
                log "job ${jobid} ainda nao apareceu em listjobs; aguardando"
                sleep 20
                ;;
            *)
                log "job ${jobid} em estado ${state}; aguardando"
                sleep 20
                ;;
        esac
    done
}

run_processor() {
    local name="$1"
    local bin="$2"
    local input="$3"
    local output="$4"

    mkdir -p "$output"
    if ! compgen -G "${input}/*.csv" >/dev/null; then
        log "${name}: nenhum CSV em ${input}; processamento ignorado"
        return 1
    fi
    if [ ! -x "$bin" ]; then
        log "${name}: executavel nao encontrado em ${bin}"
        return 1
    fi

    log "${name}: processando ${input} -> ${output}"
    "$bin" --input "$input" --output "$output"
}

log "===== inicio do pipeline ====="

BC_STATUS="falhou"
if bc_job="$(schedule_spider bugcrowdscraper engagementspider)"; then
    if wait_for_job bugcrowdscraper "$bc_job"; then
        BC_STATUS="ok"
    fi
fi

# "algumas horas depois" - tempo entre o fim do Bugcrowd e o inicio do HackerOne.
if [ -z "${H1_DELAY_SECONDS:-}" ]; then
    H1_DELAY_SECONDS="$(awk -v h="$H1_DELAY_HOURS" 'BEGIN { printf "%d", h * 3600 }')"
fi
case "$H1_DELAY_SECONDS" in
    ''|*[!0-9]*)
        log "H1_DELAY_SECONDS invalido: ${H1_DELAY_SECONDS}; usando 0"
        H1_DELAY_SECONDS=0
        ;;
esac

log "aguardando ${H1_DELAY_SECONDS}s (${H1_DELAY_HOURS}h) antes do HackerOne"
sleep "$H1_DELAY_SECONDS"

H1_STATUS="falhou"
if h1_job="$(schedule_spider hackeronescraper scopesspider)"; then
    if wait_for_job hackeronescraper "$h1_job"; then
        H1_STATUS="ok"
    fi
fi

log "processando resultados"
run_processor "Bugcrowd" "/opt/BugcrowdCsvGrabber/venv/bin/BugcrowdCsvGrabber" \
    "/output/bugcrowd" "/output/processed" || true
run_processor "HackerOne" "/opt/HackerOneCsvGrabber/venv/bin/HackerOneCsvGrabber" \
    "/output/hackerone" "/output/h1_processed" || true

log "gerando lista de dominios com wildcard"
python3 /opt/scripts/aggregate_wildcards.py \
    --output "/output/scopes/all_scope_wildcards.txt" \
    --plain-output "/output/scopes/all_scope_domains.txt" || true

log "publicando snapshots"
/opt/scripts/publish_snapshots.sh || true

log "notificando diferencas"
notify_args=()
if [ -z "${DISCORD_WEBHOOK:-}" ]; then
    notify_args+=(--no-notify)
fi
/opt/scripts/notify_diff.sh /output/snapshots "${notify_args[@]}" || true

SUMMARY="Pipeline finalizado: Bugcrowd=${BC_STATUS} | HackerOne=${H1_STATUS} | wildcard: /output/scopes/all_scope_wildcards.txt"
log "$SUMMARY"
notify_msg "$SUMMARY"

# Garante que os arquivos gerados pertençam ao usuário do host (bind mount ./data),
# mesmo quando o pipeline roda como root dentro do container.
if [ -n "${PUID:-}" ] && [ -n "${PGID:-}" ]; then
    chown -R "${PUID}:${PGID}" /output 2>/dev/null || true
fi

log "===== fim do pipeline ====="
