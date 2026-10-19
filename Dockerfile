# syntax=docker/dockerfile:1

FROM python:3.12-slim

ARG DEBIAN_FRONTEND=noninteractive
ARG NOTIFY_VERSION=1.0.7

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    SCRAPYD_URL=http://127.0.0.1:6800 \
    BUGCROWD_OUTPUT_DIR=/output/bugcrowd \
    HACKERONE_OUTPUT_DIR=/output/hackerone \
    H1_DELAY_HOURS=3 \
    JOB_TIMEOUT_SECONDS=21600 \
    TZ=America/Sao_Paulo

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        cron \
        curl \
        jq \
        tzdata \
        unzip \
        util-linux \
    && rm -rf /var/lib/apt/lists/*

# notify (projectdiscovery) - usado pelo notify_diff.sh
RUN set -eux; \
    arch="$(dpkg --print-architecture)"; \
    case "$arch" in \
        amd64) narch=amd64 ;; \
        arm64) narch=arm64 ;; \
        armhf) narch=arm ;; \
        i386)  narch=386 ;; \
        *) echo "arquitetura nao suportada: $arch" >&2; exit 1 ;; \
    esac; \
    base="https://github.com/projectdiscovery/notify/releases/download/v${NOTIFY_VERSION}"; \
    curl -fsSL --retry 3 "${base}/notify_${NOTIFY_VERSION}_linux_${narch}.zip" -o "/tmp/notify_${NOTIFY_VERSION}_linux_${narch}.zip"; \
    curl -fsSL --retry 3 "${base}/notify_${NOTIFY_VERSION}_checksums.txt" -o /tmp/notify.checksums; \
    (cd /tmp && grep "notify_${NOTIFY_VERSION}_linux_${narch}.zip$" notify.checksums | sha256sum -c -); \
    unzip -oq "/tmp/notify_${NOTIFY_VERSION}_linux_${narch}.zip" -d /usr/local/bin; \
    chmod +x /usr/local/bin/notify; \
    rm -f "/tmp/notify_${NOTIFY_VERSION}_linux_${narch}.zip" /tmp/notify.checksums; \
    notify -version -disable-update-check

# Dependencias dos scrapers (Scrapyd + Scrapy + client)
RUN pip install --no-cache-dir \
        "Scrapy==2.14.1" \
        "scrapy-rotating-proxies==0.6.2" \
        "scrapyd==1.6.0" \
        "scrapyd-client==2.0.3" \
        "python-dotenv==1.2.1"

# Projetos Scrapy em /opt (mesmos caminhos usados pelo pipeline)
COPY bugcrowdscraper /opt/BugcrowdScraper
COPY HackerOneScraper/hackeronescraper /opt/HackerOneScraper

RUN touch /opt/BugcrowdScraper/proxies.txt /opt/HackerOneScraper/proxies.txt \
    && chmod 0644 /opt/BugcrowdScraper/proxies.txt /opt/HackerOneScraper/proxies.txt

# Ferramentas de processamento de CSV, cada uma em sua venv
COPY BugcrowdCSVGrabber /opt/BugcrowdCsvGrabber
COPY HackerOneCsvGrabber /opt/HackerOneCsvGrabber

RUN python -m venv /opt/BugcrowdCsvGrabber/venv \
    && /opt/BugcrowdCsvGrabber/venv/bin/pip install --no-cache-dir /opt/BugcrowdCsvGrabber \
    && python -m venv /opt/HackerOneCsvGrabber/venv \
    && /opt/HackerOneCsvGrabber/venv/bin/pip install --no-cache-dir /opt/HackerOneCsvGrabber

COPY scripts /opt/scripts
COPY notify_diff.sh /opt/scripts/notify_diff.sh
RUN chmod +x /opt/scripts/*.sh /opt/scripts/*.py \
    && mkdir -p /output/bugcrowd /output/hackerone /output/processed \
                /output/h1_processed /output/snapshots /output/scopes /output/logs \
                /var/log/scrapyd

WORKDIR /opt
EXPOSE 6800

ENTRYPOINT ["/opt/scripts/entrypoint.sh"]
