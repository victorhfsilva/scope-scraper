#!/usr/bin/env python3
"""Consolida os dominios encontrados nos CSVs processados e gera:

  - all_scope_wildcards.txt  -> *.example.com (um por linha)
  - all_scope_domains.txt    -> example.com    (lista sem wildcard)

O arquivo e gravado dentro de /output, que no docker-compose e o bind mount
./data do host.
"""
from __future__ import annotations

import argparse
import ipaddress
import re
import sys
from pathlib import Path

DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)"
    r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z]{2,63}$",
    re.IGNORECASE,
)

SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)


def normalize(raw: str) -> str | None:
    value = raw.strip()
    if not value or value.startswith("#"):
        return None

    # Muitos CSV trazem descricoes junto; usa o primeiro token.
    value = value.split()[0]
    value = SCHEME_RE.sub("", value)

    # Emails e formatos com userinfo nao sao dominios de escopo.
    if "@" in value:
        return None

    # Remove path/query/fragment.
    value = re.split(r"[/?#]", value, maxsplit=1)[0]
    value = value.strip().strip(".")

    # Normaliza wildcard.
    value = value.lower()
    while value.startswith("*."):
        value = value[2:]
    value = value.lstrip("*.").strip()

    # Remove porta (mas nao IPv6).
    if value.count(":") == 1:
        host, _, port = value.partition(":")
        if port.isdigit():
            value = host

    value = value.rstrip(".").strip()
    if not value:
        return None

    # Descarta IPs e redes.
    try:
        ipaddress.ip_network(value, strict=False)
        return None
    except ValueError:
        pass

    if not DOMAIN_RE.match(value):
        return None

    return value


def iter_lines(paths: list[Path]):
    for path in paths:
        try:
            with path.open("r", encoding="utf-8", errors="replace") as handle:
                for line in handle:
                    yield line
        except OSError as exc:
            print(f"[aggregate] ignorando {path}: {exc}", file=sys.stderr)


def collect(base: Path, patterns: list[str]) -> set[str]:
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(sorted(base.glob(pattern)))

    domains: set[str] = set()
    for line in iter_lines(paths):
        domain = normalize(line)
        if domain:
            domains.add(domain)
    return domains


def write_lines(path: Path, values: set[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        for value in sorted(values):
            handle.write(value + "\n")
    tmp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bugcrowd", default="/output/processed")
    parser.add_argument("--hackerone", default="/output/h1_processed")
    parser.add_argument("--output", default="/output/scopes/all_scope_wildcards.txt")
    parser.add_argument("--plain-output", default="/output/scopes/all_scope_domains.txt")
    args = parser.parse_args()

    bugcrowd = collect(Path(args.bugcrowd), [
        "*_cleaned_domains.txt",
        "*_rough_websites.txt",
        "*_rough_apis.txt",
    ])
    hackerone = collect(Path(args.hackerone), [
        "*_cleaned_urls.txt",
        "*_wildcards_domains.txt",
        "*_rough_urls.txt",
        "*_rough_wildcards.txt",
    ])

    domains = bugcrowd | hackerone
    wildcards = {f"*.{domain}" for domain in domains}

    write_lines(Path(args.output), wildcards)
    write_lines(Path(args.plain_output), domains)

    print(
        f"[aggregate] Bugcrowd={len(bugcrowd)} HackerOne={len(hackerone)} "
        f"combinados={len(domains)} -> {args.output}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
