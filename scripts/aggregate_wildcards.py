#!/usr/bin/env python3
"""Consolida os dominios encontrados nos CSVs processados e gera:

  - all_scope_wildcards.txt  -> *.example.com (um por linha)
  - all_scope_domains.txt    -> example.com    (lista sem wildcard)
  - all_scope_wildcards_new.txt -> wildcards novos (nao presentes no arquivo anterior)
  - all_scope_domains_new.txt   -> dominios novos  (nao presentes no arquivo anterior)

Os arquivos sao gravados dentro de /output, que no docker-compose e o bind
mount ./data do host. A cada execucao, os arquivos *_new.txt sao recalculados
comparando o escopo atual com o arquivo consolidado da execucao anterior.

Quando o escopo atual nao traz nenhum dominio novo (por exemplo, quando e
identico ao do dia anterior), os arquivos *_new.txt NAO sao sobrescritos:
permanecem inalterados com os dominios descobertos nos dias passados.

Os arquivos *_new.txt so recebem dominios completos (registraveis), como
target.com ou target.gov.br. Sufixos publicos isolados (ex.: gov.br, com.br,
co.uk), que representariam uma infinidade de subdominios, sao descartados
usando a Public Suffix List embutida no tldextract.
"""
from __future__ import annotations

import argparse
import ipaddress
import re
import sys
from pathlib import Path

import tldextract

# Extrator offline: usa apenas o snapshot da Public Suffix List embutido no
# pacote, sem fazer requisicoes de rede.
_PSL = tldextract.TLDExtract(suffix_list_urls=(), fallback_to_snapshot=True)

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


def is_complete_domain(domain: str) -> bool:
    """Indica se o dominio e registravel (eTLD+1) sob um sufixo publico.

    Rejeita sufixos publicos isolados como ``gov.br``, ``com.br`` ou ``co.uk``,
    que teriam uma infinidade de subdominios e nao sao alvos concretos.
    Aceita ``target.com``, ``target.gov.br`` e hosts especificos.
    """
    extracted = _PSL(domain)
    return bool(extracted.domain)


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


def new_path(path: Path) -> Path:
    """Deriva o caminho do arquivo de 'novos', inserindo '_new' antes da extensao."""
    return path.with_name(f"{path.stem}_new{path.suffix}")


def read_previous_domains(*paths: Path) -> set[str]:
    """Le os dominios normalizados dos arquivos consolidados da execucao anterior."""
    domains: set[str] = set()
    for path in paths:
        if not path.exists():
            continue
        for line in iter_lines([path]):
            domain = normalize(line)
            if domain:
                domains.add(domain)
    return domains


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

    raw_domains = bugcrowd | hackerone

    # Somente dominios completos (registraveis) entram nos arquivos, tanto no
    # consolidado quanto nos *_new.txt. Sufixos publicos isolados (gov.br,
    # com.br, co.uk, ...) sao descartados por representarem uma infinidade de
    # subdominios e nao um alvo concreto.
    domains = {d for d in raw_domains if is_complete_domain(d)}
    dropped = raw_domains - domains
    wildcards = {f"*.{domain}" for domain in domains}

    output = Path(args.output)
    plain_output = Path(args.plain_output)

    previous = read_previous_domains(output, plain_output)
    new_domains = domains - previous

    write_lines(output, wildcards)
    write_lines(plain_output, domains)

    new_wildcard_path = new_path(output)
    new_domain_path = new_path(plain_output)

    if new_domains:
        write_lines(new_wildcard_path, {f"*.{domain}" for domain in new_domains})
        write_lines(new_domain_path, new_domains)
    else:
        # Nada novo em relacao a execucao anterior (ex.: escopo identico ao de
        # ontem). Preserva os arquivos *_new.txt intactos para que continuem
        # mostrando os dominios descobertos nos dias passados, em vez de
        # esvazia-los. So cria um arquivo vazio se ele ainda nao existir.
        for path in (new_wildcard_path, new_domain_path):
            if not path.exists():
                write_lines(path, set())

    print(
        f"[aggregate] Bugcrowd={len(bugcrowd)} HackerOne={len(hackerone)} "
        f"combinados={len(domains)} -> {args.output}",
        file=sys.stderr,
    )
    if dropped:
        print(
            f"[aggregate] descartados {len(dropped)} sufixo(s) publico(s) "
            f"incompleto(s): {', '.join(sorted(dropped))}",
            file=sys.stderr,
        )
    if new_domains:
        print(
            f"[aggregate] novos={len(new_domains)} "
            f"(wildcards -> {new_wildcard_path}, dominios -> {new_domain_path})",
            file=sys.stderr,
        )
    else:
        print(
            f"[aggregate] novos=0; escopo sem mudancas. Arquivos *_new "
            f"preservados: {new_wildcard_path}, {new_domain_path}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
