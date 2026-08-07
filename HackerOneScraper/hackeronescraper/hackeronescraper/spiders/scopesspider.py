import scrapy
from dotenv import load_dotenv, find_dotenv
import os
import base64

load_dotenv(find_dotenv(usecwd=True))

class ScopesspiderSpider(scrapy.Spider):
    name = "scopesspider"
    start_urls = "https://api.hackerone.com/v1/hackers/programs/"

    def start_requests(self):
        headers = self._get_headers()
        yield scrapy.Request(url=self.start_urls, headers=headers, callback=self.parse_programs)

    def _get_headers(self):
        username = os.getenv("HACKERONE_USERNAME")
        token = os.getenv("HACKERONE_TOKEN")
        creds = f"{username}:{token}".encode("utf-8")
        encoded = base64.b64encode(creds).decode("utf-8")
        
        return {
            "Authorization": f"Basic {encoded}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def parse_programs(self, response):
        self.logger.info(f"Parsing programs from {response.url}")

        try:
            data = response.json()
            programs = data.get("data", [])

            for program in programs:
                program_id = program.get("id")
                program_handle = program.get("attributes", {}).get("handle")
                self.logger.debug(f"Found program: {program_handle} (ID: {program_id})")

                scopes_url = f"{self.start_urls}{program_handle}/structured_scopes"
                yield scrapy.Request(url=scopes_url, headers=self._get_headers(), callback=self.parse_scopes, meta={ "program_id": program_id, "program_handle": program_handle})

            links = data.get("links", {})
            next_url = links.get("next")

            if next_url:
                yield scrapy.Request(url=next_url, headers=self._get_headers(), callback=self.parse_programs)

        except Exception as e:
            self.logger.error(f"Error parsing programs: {e}")

    def parse_scopes(self, response):
        program_id = response.meta.get("program_id")
        program_handle = response.meta.get("program_handle")
        self.logger.debug(f"Parsing scopes for program {program_handle} (ID: {program_id}) from {response.url}")

        try:
            data = response.json()
            scopes = data.get("data", [])

            for scope in scopes:
                scope_attributes = scope.get("attributes", {})
                yield {
                    "program_id": program_id,
                    "program_handle": program_handle,
                    "scope_id": scope.get("id"),
                    "asset_type": scope_attributes.get("asset_type"),
                    "identifier": scope_attributes.get("asset_identifier"),
                    "instruction": scope_attributes.get("instruction"),
                    "eligible_for_bounty": scope_attributes.get("eligible_for_bounty"),
                    "eligible_for_submission": scope_attributes.get("eligible_for_submission"),
                    "availability_requirement": scope_attributes.get("availability_requirement"),
                    "confidentiality_requirement": scope_attributes.get("confidentiality_requirement"),
                    "integrity_requirement": scope_attributes.get("integrity_requirement"),
                    "max_severity": scope_attributes.get("max_severity"),
                    "created_at": scope_attributes.get("created_at"),
                    "updated_at": scope_attributes.get("updated_at")
                }

            links = data.get("links", {})
            next_url = links.get("next")

            if next_url:
                yield scrapy.Request(url=next_url, headers=self._get_headers(), callback=self.parse_scopes, meta={"program_id": program_id, "program_handle": program_handle})

        except Exception as e:
            self.logger.error(f"Error parsing scopes for program {program_handle} (ID: {program_id}): {e}")