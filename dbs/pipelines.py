#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys

sys.path.append("../../")

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from dbs import mongo_setting
from common.log_out import log_err


class MongoPipeline:
    def __init__(self, COLLECTION):
        if not mongo_setting.MONGO_USR and not mongo_setting.MONGO_PWD:
            client = MongoClient(f'mongodb://{mongo_setting.MONGO_HOST}:{mongo_setting.MONGO_PORT}')
        else:
            client = MongoClient(f'mongodb://{mongo_setting.MONGO_HOST}:{mongo_setting.MONGO_PORT}')
        self.coll = client[mongo_setting.MONGO_DB][COLLECTION]

    def insert_item(self, item):
        status = False
        if not item:
            return False
        elif isinstance(item, list):
            for _i in item:
                try:
                    self.coll.insert_one(_i)
                    print(_i)
                except DuplicateKeyError:
                    status = True
                except Exception as error:
                    log_err(error)
                    status = True
        elif isinstance(item, dict):
            try:
                self.coll.insert_one(item)
                print(item)
            except DuplicateKeyError:
                status = True
                pass
            except Exception as error:
                log_err(error)
                status = True
        else:
            status = False
        return status

    @staticmethod
    def field_query(model, data):
        new_data = {}
        for key in model.keys():
            new_data.update({
                key: data.get(key)
            })
        return new_data

    def update_item(self, query, item):
        if not item: return
        data = self.coll.find_one(self.field_query(query, item))
        if data:
            item['type'] = list(set(data['type'] + item['type']))
        if isinstance(item, dict):
            # print(item)
            try:
                self.coll.update_one(self.field_query(query, item), {'$set': item}, upsert=True)
            except Exception as error:
                log_err(error)

    def find(self, query):
        return self.coll.find(query)

    def find_one(self, query):
        return self.coll.find_one(query)

    def count(self, query):
        return self.coll.count_documents(query)
