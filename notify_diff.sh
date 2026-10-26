#!/usr/bin/env bash
#
# notify_diff.sh
#
# Para cada categoria (sufixo do nome do arquivo), compara o snapshot
# MAIS RECENTE com o PENÚLTIMO e notifica as mudanças encontradas.
#
# Convenção de nomes: YYYYMMDD_<categoria>.txt
#   Ex.: 20260818_cleaned_domains.txt, 20260817_rough_apis.txt
#
# Uso:
#   notify_diff.sh [DIR] [opções]
#
# Opções:
#   --no-notify        força a saída no terminal (mesmo com notify instalado)
#   --new-limit N      máx. de itens novos exibidos por categoria (padrão: 10)
#   --removed-limit N  máx. de itens removidos exibidos por categoria (padrão: 5)
#   --no-digest        não envia o resumo final via notify
#   --send-delay N     pausa, em segundos, entre cada notificação enviada ao
#                      Discord (padrão: 1). Evita o erro 429 Too Many Requests
#                      quando várias categorias mudam na mesma execução.
#   -h, --help         mostra esta ajuda
#
# Dependências opcionais: notify (projectdiscovery) para as notificações.

set -euo pipefail

# Colação por bytes em TODO o script: garante que 'sort -u' e 'comm'
# usem a MESMA ordem de comparação, independente do locale do shell e
# da implementação do sort (GNU, BusyBox, BSD). Sem isto, sort pode
# ordenar por bytes enquanto comm compara por colação UTF-8 (strcoll),
# gerando 'comm: input is not in sorted order' e matando o script
# (set -e). Veja: LC_ALL=C força memcmp em ambos (coreutils).
export LC_ALL=C
export LANG=C

DIR="${1:-./output}"
NEW_LIMIT=10
REMOVED_LIMIT=5
NOTIFY=auto
DIGEST=1
SEND_DELAY=1

usage() {
    cat <<'EOF'
Uso: notify_diff.sh [DIR] [opções]

Compara o snapshot mais recente com o penúltimo de cada categoria
(arquivos YYYYMMDD_<categoria>.txt) e notifica as mudanças via
'notify' (projectdiscovery) ou no terminal como fallback.

Opções:
  --no-notify        força a saída no terminal (mesmo com notify instalado)
  --new-limit N      máx. de itens novos exibidos por categoria (padrão: 10)
  --removed-limit N  máx. de itens removidos exibidos por categoria (padrão: 5)
  --no-digest        não envia o resumo final via notify
  --send-delay N     pausa (segundos) entre notificações do Discord (padrão: 1)
  -h, --help         mostra esta ajuda
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
        --no-notify)     NOTIFY=no ;;
        --new-limit)     NEW_LIMIT="${2:?--new-limit requer um valor}"; shift ;;
        --removed-limit) REMOVED_LIMIT="${2:?--removed-limit requer um valor}"; shift ;;
        --no-digest)     DIGEST=0 ;;
        --send-delay)    SEND_DELAY="${2:?--send-delay requer um valor}"; shift ;;
        -h|--help)       usage; exit 0 ;;
        -*)              echo "Opção desconhecida: $1" >&2; usage >&2; exit 1 ;;
        *)               DIR="$1" ;;
    esac
    shift
done

case "$NEW_LIMIT" in
    ''|*[!0-9]*) echo "--new-limit deve ser um número (0 desativa a prévia)" >&2; exit 1 ;;
esac
case "$REMOVED_LIMIT" in
    ''|*[!0-9]*) echo "--removed-limit deve ser um número (0 desativa a prévia)" >&2; exit 1 ;;
esac
case "$SEND_DELAY" in
    ''|*[!0-9]*) echo "--send-delay deve ser um número (em segundos)" >&2; exit 1 ;;
esac

[ -d "$DIR" ] || { echo "Diretório não encontrado: $DIR" >&2; exit 1; }
[ -r "$DIR" ] || { echo "Sem permissão de leitura: $DIR" >&2; exit 1; }

shopt -s nullglob

# ----------------------------------------------------------------------
# funções auxiliares
# ----------------------------------------------------------------------

# 1234 -> 1.234 (separador de milhar, pt-BR)
fmt_num() {
    local n="$1" out="" tail
    while [ "${#n}" -gt 3 ]; do
        tail="${n: -3}"
        out=".${tail}${out}"
        n="${n:0:${#n}-3}"
    done
    echo "${n}${out}"
}

# variação percentual com sinal: pct <parte> <base> [sinal]  ->  +13,6%
pct() {
    local part="$1" base="$2" sign="${3:-+}" tenths
    if [ "$base" -eq 0 ]; then
        if [ "$part" -gt 0 ]; then echo "${sign}100,0%"; else echo "+0,0%"; fi
        return
    fi
    tenths=$(( part * 1000 / base ))
    if [ "$sign" = "-" ]; then
        echo "-$(( tenths / 10 )),$(( tenths % 10 ))%"
    else
        echo "+$(( tenths / 10 )),$(( tenths % 10 ))%"
    fi
}

# 20260818 -> 2026-08-18 (mantém o original se a data for inválida)
fmt_date() {
    date -d "$1" +%Y-%m-%d 2>/dev/null || echo "$1"
}

# rótulo amigável por categoria
declare -A LABELS=(
    [cleaned_domains.txt]="Domínios limpos"
    [cleaned_ips.txt]="IPs limpos"
    [rough_websites.txt]="Websites brutos"
    [rough_other_assets.txt]="Outros ativos brutos"
    [rough_networks.txt]="Redes brutas"
    [rough_ip_addresses.txt]="Endereços IP brutos"
    [rough_iot.txt]="Dispositivos IoT brutos"
    [rough_android.txt]="Apps Android brutos"
    [rough_apis.txt]="APIs brutas"
    [rough_hardware.txt]="Hardware bruto"
    [rough_ios.txt]="Apps iOS brutos"

    [bugcrowd_cleaned_domains.txt]="Bugcrowd - domínios limpos"
    [bugcrowd_cleaned_ips.txt]="Bugcrowd - IPs limpos"
    [bugcrowd_rough_websites.txt]="Bugcrowd - websites brutos"
    [bugcrowd_rough_apis.txt]="Bugcrowd - APIs brutas"
    [bugcrowd_rough_ip_addresses.txt]="Bugcrowd - IPs brutos"
    [bugcrowd_rough_networks.txt]="Bugcrowd - redes brutas"
    [bugcrowd_rough_other_assets.txt]="Bugcrowd - outros ativos"
    [bugcrowd_rough_ios.txt]="Bugcrowd - iOS"
    [bugcrowd_rough_android.txt]="Bugcrowd - Android"
    [bugcrowd_rough_hardware.txt]="Bugcrowd - hardware"
    [bugcrowd_rough_iot.txt]="Bugcrowd - IoT"

    [hackerone_cleaned_urls.txt]="HackerOne - URLs limpas"
    [hackerone_wildcards_domains.txt]="HackerOne - wildcards"
    [hackerone_rough_urls.txt]="HackerOne - URLs brutas"
    [hackerone_rough_wildcards.txt]="HackerOne - wildcards brutos"
    [hackerone_rough_ip_addresses.txt]="HackerOne - IPs brutos"
    [hackerone_rough_ip_ranges.txt]="HackerOne - faixas de IP"
    [hackerone_expanded_ip_addresses.txt]="HackerOne - IPs expandidos"
    [hackerone_source_code_repos.txt]="HackerOne - repositórios"
    [hackerone_apple_store_app_ids.txt]="HackerOne - apps iOS"
    [hackerone_google_play_app_ids.txt]="HackerOne - apps Android"

    [all_scope_wildcards.txt]="Escopo combinado - domínios com wildcard"
)

label_for() { echo "${LABELS[${1:-}]:-${1:-}}"; }

# envia a mensagem (notify) ou imprime no terminal (fallback)
send() {
    if [ "$NOTIFY" = yes ]; then
        printf '%s\n' "$1" | notify -disable-update-check || true
        # Evita o 429 do Discord quando várias categorias mudam na mesma execução.
        [ "$SEND_DELAY" -gt 0 ] && sleep "$SEND_DELAY"
    else
        printf '%s\n' "$1"
    fi
}

# ----------------------------------------------------------------------
# detecção do notify
# ----------------------------------------------------------------------
if [ "$NOTIFY" = auto ]; then
    if command -v notify >/dev/null 2>&1; then
        NOTIFY=yes
        echo "notify encontrado - notificações serão enviadas" >&2
    else
        NOTIFY=no
        echo "notify não encontrado no PATH - exibindo no terminal" >&2
    fi
fi

# ----------------------------------------------------------------------
# coleta das categorias
# ----------------------------------------------------------------------
keys=()
for f in "$DIR"/[0-9]*_*.txt; do
    [ -f "$f" ] || continue
    bn=$(basename "$f")
    keys+=("${bn#*_}")          # tudo após a data (categoria + extensão)
done

if [ "${#keys[@]}" -eq 0 ]; then
    echo "Nenhum arquivo YYYYMMDD_*.txt encontrado em $DIR" >&2
    exit 0
fi

mapfile -t uniq_keys < <(printf '%s\n' "${keys[@]}" | sort -u)

# ----------------------------------------------------------------------
# comparação: mais recente vs. penúltimo (por categoria)
# ----------------------------------------------------------------------
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

changes=0
unchanged=0
no_history=0
total_new=0
total_removed=0
changed_keys=()

for key in "${uniq_keys[@]}"; do
    files=()
    for f in "$DIR"/[0-9]*_"$key"; do
        [ -f "$f" ] || continue
        files+=("$f")
    done
    mapfile -t files < <(printf '%s\n' "${files[@]}" | sort -r)

    if [ "${#files[@]}" -lt 2 ]; then
        no_history=$((no_history + 1))
        echo "[skip] ${key}: apenas 1 snapshot (sem histórico)" >&2
        continue
    fi

    latest="${files[0]}"
    prev="${files[1]}"
    bn_latest=$(basename "$latest")
    bn_prev=$(basename "$prev")
    date_latest="${bn_latest%%_*}"
    date_prev="${bn_prev%%_*}"

    # normaliza: remove linhas vazias, deduplica e ordena
    sed '/^[[:space:]]*$/d' "$latest" | sort -u >"$tmpdir/latest"
    sed '/^[[:space:]]*$/d' "$prev"   | sort -u >"$tmpdir/prev"

    latest_total=$(wc -l <"$latest" | tr -d ' ')
    prev_total=$(wc -l <"$prev"   | tr -d ' ')
    latest_uniq=$(wc -l <"$tmpdir/latest" | tr -d ' ')
    prev_uniq=$(wc -l <"$tmpdir/prev" | tr -d ' ')

    comm -23 "$tmpdir/latest" "$tmpdir/prev" >"$tmpdir/new"       # só no recente
    comm -13 "$tmpdir/latest" "$tmpdir/prev" >"$tmpdir/removed"   # só no anterior

    new_count=$(wc -l <"$tmpdir/new" | tr -d ' ')
    removed_count=$(wc -l <"$tmpdir/removed" | tr -d ' ')
    kept=$(( prev_uniq - removed_count ))

    if [ "$new_count" -eq 0 ] && [ "$removed_count" -eq 0 ]; then
        unchanged=$((unchanged + 1))
        echo "[ok] ${key}: sem mudanças (${prev_uniq} itens estáveis)" >&2
        continue
    fi

    changes=$((changes + 1))
    total_new=$((total_new + new_count))
    total_removed=$((total_removed + removed_count))
    changed_keys+=("$key")

    # limites das prévias
    shown_new=0; more_new=0
    shown_removed=0; more_removed=0
    if [ "$new_count" -gt 0 ] && [ "$NEW_LIMIT" -gt 0 ]; then
        shown_new=$(( new_count < NEW_LIMIT ? new_count : NEW_LIMIT ))
        more_new=$(( new_count - shown_new ))
    fi
    if [ "$removed_count" -gt 0 ] && [ "$REMOVED_LIMIT" -gt 0 ]; then
        shown_removed=$(( removed_count < REMOVED_LIMIT ? removed_count : REMOVED_LIMIT ))
        more_removed=$(( removed_count - shown_removed ))
    fi

    # intervalo entre as coletas (detecta lacuna de histórico)
    gap_line=""
    if ts1=$(date -d "$date_latest" +%s 2>/dev/null) && ts2=$(date -d "$date_prev" +%s 2>/dev/null); then
        gap_days=$(( (ts1 - ts2) / 86400 ))
        gap_line="Intervalo entre coletas: ${gap_days} dia(s)"
        [ "$gap_days" -gt 1 ] && gap_line="${gap_line} - ATENÇÃO: lacuna no histórico"
    fi

    label=$(label_for "$key")
    msg=$(printf '%s\n' \
"============================================================
[ ${label} ] mudanças detectadas
============================================================
Snapshot recente : ${bn_latest}  (${date_latest} -> $(fmt_date "$date_latest"))
Snapshot anterior: ${bn_prev}  (${date_prev} -> $(fmt_date "$date_prev"))
${gap_line}

Estatísticas:
  ${bn_latest}
    linhas: $(fmt_num "$latest_total")   únicos: $(fmt_num "$latest_uniq")
  ${bn_prev}
    linhas: $(fmt_num "$prev_total")   únicos: $(fmt_num "$prev_uniq")
  [+] Novos     : $(fmt_num "$new_count")  ($(pct "$new_count" "$prev_uniq") em relação ao anterior)
  [-] Removidos : $(fmt_num "$removed_count")  ($(pct "$removed_count" "$prev_uniq" -) em relação ao anterior)
  [=] Mantidos  : $(fmt_num "$kept")")

    # seção de itens novos
    if [ "$new_count" -gt 0 ]; then
        if [ "$shown_new" -gt 0 ]; then
            preview_new=$(sed -n "1,${shown_new}p" "$tmpdir/new" | awk '{printf "  %d) %s\n", NR, $0}')
            new_section=$(printf '\n\n--- Novos itens (%s de %s) ---\n%s\n' \
                "$shown_new" "$(fmt_num "$new_count")" "$preview_new")
            [ "$more_new" -gt 0 ] && new_section+=$(printf '\n  ... e mais %s itens não exibidos' "$(fmt_num "$more_new")")
        else
            new_section=$(printf '\n\n(prévia desativada - total de novos: %s)' "$(fmt_num "$new_count")")
        fi
        msg+="$new_section"
    fi

    # seção de itens removidos
    if [ "$removed_count" -gt 0 ]; then
        if [ "$shown_removed" -gt 0 ]; then
            preview_removed=$(sed -n "1,${shown_removed}p" "$tmpdir/removed" | awk '{printf "  %d) %s\n", NR, $0}')
            removed_section=$(printf '\n\n--- Itens removidos (%s de %s) ---\n%s\n' \
                "$shown_removed" "$(fmt_num "$removed_count")" "$preview_removed")
            [ "$more_removed" -gt 0 ] && removed_section+=$(printf '\n  ... e mais %s itens não exibidos' "$(fmt_num "$more_removed")")
        else
            removed_section=$(printf '\n\n(prévia desativada - total de removidos: %s)' "$(fmt_num "$removed_count")")
        fi
        msg+="$removed_section"
    fi

    send "$msg"
    if [ "$NOTIFY" = yes ]; then
        printf '[notify] %s: +%s novos, -%s removidos\n' \
            "$label" "$(fmt_num "$new_count")" "$(fmt_num "$removed_count")"
    fi
done

# ----------------------------------------------------------------------
# resumo final
# ----------------------------------------------------------------------
digest=$(printf '%s\n' \
"============================================================
RESUMO DA EXECUÇÃO - notify_diff
============================================================
Diretório : ${DIR}
Executado : $(date '+%Y-%m-%d %H:%M:%S')
Categorias: ${#uniq_keys[@]} total (${changes} com mudanças | ${unchanged} sem mudanças | ${no_history} sem histórico)
Novos     : $(fmt_num "$total_new") itens
Removidos : $(fmt_num "$total_removed") itens")
if [ "$changes" -gt 0 ]; then
    digest+=$'\n\nCategorias com mudanças:'
    for k in "${changed_keys[@]}"; do
        digest+=$'\n  - '"$(label_for "$k")"
    done
fi

if [ "$DIGEST" -eq 1 ] && [ "$changes" -gt 0 ]; then
    send "$digest"
elif [ "$NOTIFY" = no ]; then
    printf '%s\n' "$digest"
fi

printf '[notify_diff] %s categorias | %s com mudanças | +%s novos | -%s removidos\n' \
    "${#uniq_keys[@]}" "$changes" "$(fmt_num "$total_new")" "$(fmt_num "$total_removed")" >&2

exit 0
