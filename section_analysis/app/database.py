# -*- coding: utf-8 -*-

import os
from pymongo import MongoClient, ASCENDING

MONGO_DB_ADDR = os.getenv('MONGO_DB_ADDR', 'localhost')


class MongodbService(object):
    _instance = None
    _client = None
    _db = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls.__init__(cls._instance, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self._client = MongoClient(MONGO_DB_ADDR, 27017)
        self._db = self._client.section_analysis
        self._db.sections.create_index([('expired_at', ASCENDING)], expireAfterSeconds=0)

    def get_data(self, analyzed_section_base_name):
        return self._db.sections.find_one({'analyzed_section_base_name': analyzed_section_base_name})

    def save_data(self, section):
        self._db.sections.insert_one(section)
