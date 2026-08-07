## Bugcrowd Scraper

![BugcrowdScraper](./img/BugcrowdScraper.png)

<div align="center">

![last commit](https://img.shields.io/github/last-commit/tyto-sec/BugcrowdScraper) ![created](https://img.shields.io/github/created-at/tyto-sec/BugcrowdScraper) ![language](https://img.shields.io/github/languages/top/tyto-sec/BugcrowdScraper) ![stars](https://img.shields.io/github/stars/tyto-sec/BugcrowdScraper)

</div>

> Bugcrowd Scraper is a Python tool that collects engagement data and scope targets from Bugcrowd and exports structured items using Scrapy feeds.

<br>

## Features

*   Collects engagements from the Bugcrowd public listings endpoint
*   Follows each engagement brief to fetch scope details
*   Automatic pagination across engagement pages
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
curl http://localhost:6800/schedule.json -d "project=bugcrowdscraper" -d "spider=engagementspider"
```

<br>

## Output

Items are exported according to the FEEDS setting in Scrapy or via spider run parameters.

