#!/usr/bin/env bash
#
# Copia os arquivos YYYYMMDD_<categoria>.txt processados para /output/snapshots
# com o prefixo da plataforma. Isso evita colisao entre categorias iguais
# (ex.: rough_ip_addresses do Bugcrowd e do HackerOne) no notify_diff.sh.
#
set -euo pipefail

SNAP="/output/snapshots"
mkdir -p "$SNAP"

shopt -s nullglob

copy_platform() {
    local platform="$1"
    local dir="$2"
    local file base date category

    [ -d "$dir" ] || return 0
    for file in "$dir"/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_*.txt; do
        base="$(basename "$file")"
        date="${base%%_*}"
        category="${base#*_}"
        cp -f "$file" "${SNAP}/${date}_${platform}_${category}"
    done
}

copy_platform bugcrowd /output/processed
copy_platform hackerone /output/h1_processed

# Snapshot diario da lista combinada de wildcards, para o diff tambem
# acompanhar mudancas no escopo consolidado.
if [ -f /output/scopes/all_scope_wildcards.txt ]; then
    cp -f /output/scopes/all_scope_wildcards.txt \
        "${SNAP}/$(date +%Y%m%d)_all_scope_wildcards.txt"
fi
