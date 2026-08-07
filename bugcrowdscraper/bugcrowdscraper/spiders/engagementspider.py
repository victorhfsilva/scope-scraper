import html
import json
import math
from urllib.parse import parse_qs, urlparse

import scrapy


class EngagementspiderSpider(scrapy.Spider):
    name = "engagementspider"
    start_urls = ["https://bugcrowd.com/engagements.json?page=1"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_engagements)

    def parse_engagements(self, response):
        data = response.json()
        engagements = data.get("engagements", [])
        for engagement in engagements:

            programName =  engagement.get("name")
            programBriefUrl = engagement.get("briefUrl")
            programIndustryName = engagement.get("industryName")
            programIsPrivate = engagement.get("isPrivate")
            programScopeRank = engagement.get("scopeRank")
            reward_summary = engagement.get("rewardSummary") or {}
            programMinReward = reward_summary.get("minReward")
            programMaxReward = reward_summary.get("maxReward")

            engagement_url = f"https://bugcrowd.com{programBriefUrl}"
            yield scrapy.Request(url=engagement_url, callback=self.parse_engagement, meta= {
                "programName": programName,
                "programBriefUrl": programBriefUrl,
                "programIndustryName": programIndustryName,
                "programIsPrivate": programIsPrivate,
                "programScopeRank": programScopeRank,
                "programMinReward": programMinReward,
                "programMaxReward": programMaxReward
            })
            

        paginationMeta = data.get("paginationMeta", {})
        limit = paginationMeta.get("limit", 24)
        total_count = (
            paginationMeta.get("totalCount")
            or 0
        )

        total_pages = math.ceil(total_count / limit) if limit else 1
        current_page = self._get_current_page(response.url)

        if current_page < total_pages:
            next_page = current_page + 1
            next_url = f"https://bugcrowd.com/engagements.json?page={next_page}"
            yield scrapy.Request(url=next_url, callback=self.parse_engagements)

    def _get_current_page(self, url):
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        page_str = (query.get("page") or ["1"])[0]
        try:
            page = int(page_str)
        except ValueError:
            page = 1
        return page

    def parse_engagement(self, response):
        api_endpoints_raw = response.css(
            "div#researcher-engagement-brief-root::attr(data-api-endpoints)"
        ).get()
        brief_version_url = None

        if api_endpoints_raw:
            try:
                api_endpoints = json.loads(html.unescape(api_endpoints_raw))
                brief_version_url = (
                    api_endpoints.get("engagementBriefApi", {})
                    .get("getBriefVersionDocument")
                )
                if brief_version_url:
                    brief_version_url = response.urljoin(brief_version_url)
                    if not brief_version_url.endswith(".json"):
                        brief_version_url = f"{brief_version_url}.json"
            except json.JSONDecodeError:
                brief_version_url = None

        if not brief_version_url:
            self.logger.debug(
                "briefVersionUrl not found for %s",
                response.meta.get("programBriefUrl"),
            )
            return

        engagement_details_url = response.urljoin(brief_version_url)

        yield scrapy.Request(
            url=engagement_details_url,
            callback=self.parse_engagement_details,
            meta={
                "programName": response.meta.get("programName"),
                "programBriefUrl": response.meta.get("programBriefUrl"),
                "programIndustryName": response.meta.get("programIndustryName"),
                "programIsPrivate": response.meta.get("programIsPrivate"),
                "programScopeRank": response.meta.get("programScopeRank"),
                "programMinReward": response.meta.get("programMinReward"),
                "programMaxReward": response.meta.get("programMaxReward"),
                "briefVersionUrl": brief_version_url,
            }
        )

    def parse_engagement_details(self, response):
        data = response.json()

        engagement_data = data.get("data", {})

        engagement_scope = engagement_data.get("scope", [])

        for scope in engagement_scope:
            for target in scope.get("targets", []):
                yield {
                    "programName": response.meta.get("programName"),
                    "programBriefUrl": response.meta.get("programBriefUrl"),
                    "programIndustryName": response.meta.get("programIndustryName"),
                    "programIsPrivate": response.meta.get("programIsPrivate"),
                    "programScopeRank": response.meta.get("programScopeRank"),
                    "programMinReward": response.meta.get("programMinReward"),
                    "programMaxReward": response.meta.get("programMaxReward"),
                    "briefVersionUrl": response.meta.get("briefVersionUrl"),
                    "scopeId": scope.get("id"),
                    "scopeName": scope.get("name"),
                    "targetId": target.get("id"),
                    "targetUri": target.get("uri"),
                    "targetName": target.get("name"),
                    "targetIpAddress": target.get("ipAddress"),
                    "targetCategory": target.get("category"),
                    "targetDescription": target.get("description"),
                    "inScope": scope.get("inScope"),
                }

