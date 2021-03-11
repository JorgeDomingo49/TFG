# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class YtcItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = Field()
    url = Field()
    viewcount = Field()
    owner = Field()
    subcount = Field()
    desc = Field()
    date = Field()
    likecount = Field()
    dislikecount = Field()

    title_ad=Field()
    url_ad=Field()

class YtcRec(scrapy.Item):
    url = Field()
    rec_url = Field()
    title = Field()
    rec_channel = Field()
    rec_views = Field()
    
    date_upload = Field()

    rec_titlepubli= Field()
    rec_urlpubli = Field()

class YtcCookie(scrapy.Item):
    domain = Field()
    expires = Field()
    httpOnly = Field()
    name = Field()
    path = Field()
    secure = Field()
    value = Field()
