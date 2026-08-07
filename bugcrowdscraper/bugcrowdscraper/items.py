# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BugcrowdscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    programName = scrapy.Field()
    programBriefUrl = scrapy.Field()
    programIndustryName = scrapy.Field()
    programIsPrivate = scrapy.Field()
    programScopeRank = scrapy.Field()
    programMinReward = scrapy.Field()
    programMaxReward = scrapy.Field()
    briefVersionUrl = scrapy.Field()
    scopeId = scrapy.Field()
    scopeName = scrapy.Field()
    targetId = scrapy.Field()
    targetUri = scrapy.Field()
    targetName = scrapy.Field()
    targetIpAddress = scrapy.Field()
    targetCategory = scrapy.Field()
    targetDescription = scrapy.Field()
    inScope = scrapy.Field()
