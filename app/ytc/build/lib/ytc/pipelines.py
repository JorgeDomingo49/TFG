# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import pymongo
from urllib.parse import quote_plus
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import DropItem
import logging
from ytc.items import YtcRec,YtcItem, YtcCookie
import time

settings = get_project_settings()

class MongoDBPipeline(object):
    collections = None
    def __init__(self):
        user = settings['MONGODB_USER']
        password = settings['MONGODB_PASS']
        host = settings['MONGODB_SERVER']
        port = settings['MONGODB_PORT']
        uri = "mongodb://%s:%s@%s:%u" % (quote_plus(user), quote_plus(password), host,port)
        connection = pymongo.MongoClient(uri)
        db = connection[settings['MONGODB_DB']]
        self.collections = {
                           YtcRec : db['rec'],
                           YtcItem : db['current'],
                           YtcCookie : db['cookies']
                        }


    def process_item(self, item, spider):
        valid = True
        for c in self.collections.keys():
            if isinstance(item,c):
                collection =  self.collections[c]

        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            new_item = dict(item)
            new_item['timestamp']=time.time()
            new_item['profile']=spider.profile
            new_item['exp_id']=spider.exp_id
            collection.insert(new_item)
        return item


class YtcPipeline(object):
    def process_item(self, item, spider):
        return item
