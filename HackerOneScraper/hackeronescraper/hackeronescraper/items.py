# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HackeronescraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    program_id = scrapy.Field()
    program_handle = scrapy.Field()
    scope_id = scrapy.Field()
    identifier = scrapy.Field()
    asset_type = scrapy.Field()
    instruction = scrapy.Field()
    eligible_for_bounty = scrapy.Field()
    eligible_for_submission = scrapy.Field()
    availability_requirement = scrapy.Field()
    confidentiality_requirement = scrapy.Field()
    integrity_requirement = scrapy.Field()
    max_severity = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()