## HackerOne Scraper

![HackerOneScraper](./img/HackerOneScraper.png)

<div align="center">

![last commit](https://img.shields.io/github/last-commit/tyto-sec/HackerOneScraper) ![created](https://img.shields.io/github/created-at/tyto-sec/HackerOneScraper) ![language](https://img.shields.io/github/languages/top/tyto-sec/HackerOneScraper) ![stars](https://img.shields.io/github/stars/tyto-sec/HackerOneScraper)

</div>

> HackerOneScraper is a Python tool that collects program scopes from the HackerOne API and exports the structured items to CSV files.

<br>

## Features

*   Collects programs and scopes via the HackerOne API
*   Automatic pagination for programs and scopes
*   Credential-based auth via .env
*   Rotating proxy support via proxies.txt
*   Deploy and run with Scrapyd + ScrapydWeb

<br>

## Requirements

* Python 3.11+
* Scrapyd and Scrapyd Client
* ScrapydWeb and Logparser (optional, recommended)

<br>

## Installation

```bash
pip install -r requirements.txt
```

<br>

## Configuration

### .env

Create a .env file with your HackerOne credentials:

```
HACKERONE_USERNAME=your_username
HACKERONE_TOKEN=your_token
```

### proxies.txt

Add proxies in the following format:

```
username:password@ip:port
```

<br>

## Deploy with Scrapyd

Install deploy dependencies:

```bash
pip install scrapyd scrapyd-client
```

Start Scrapyd:

```bash
scrapyd
```

Deploy the project:

```bash
scrapyd-client deploy
```

<br>

## ScrapyWeb (optional)

Install the web panel:

```bash
pip install scrapydweb logparser
```

Start the services:

```bash
scrapyd &
scrapydweb &
logparser &
```

<br>

## Scrapyd API

*   POST /schedule.json → Run spider
*   GET  /listspiders.json → List spiders
*   GET  /listprojects.json → Projects
*   GET  /listjobs.json → Active jobs
*   POST /cancel.json → Stop job

<br>

## Run

To schedule the spider via API:

```bash
curl http://localhost:6800/schedule.json -d "project=hackeronescraper" -d "spider=scopesspider"
```

<br>

## Output

Items are exported according to the FEEDS setting in Scrapy or via spider run parameters.

