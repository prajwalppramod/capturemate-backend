import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from bson.objectid import ObjectId
from utils import Singleton

class StorageConnection(metaclass=Singleton):
    def __init__(self):
        self.db_name = 'capturemate'
        self.client = MongoClient(os.environ.get('DB_URI', 'mongodb://localhost:27017'), server_api=ServerApi('1'))
        self.db_handle = self.client[self.db_name]
        print('Connected to database')
    
    def get_collection(self, collection_name: str) -> Collection:
        return self.db_handle[collection_name]
    
    def insert_document(self, collection_name: str, document: any):
        collection = self.get_collection(collection_name)
        return collection.insert_one(document)
    
    def find_document_by_id(self, collection_name: str, document_id: str):
        collection = self.get_collection(collection_name)
        return collection.find_one({'_id': ObjectId(document_id)})
    
    def find_document(self, collection_name: str, query: dict):
        collection = self.get_collection(collection_name)
        return collection.find_one(query)
    
    def find_documents(self, collection_name: str, query: dict):
        collection = self.get_collection(collection_name)
        return collection.find(query)
    
    def update_document(self, collection_name: str, query: dict, update: dict, upsert=False):
        collection = self.get_collection(collection_name)
        return collection.update_one(query, update, upsert=upsert)
    
    def update_document_by_id(self, collection_name: str, document_id: str, update: dict, upsert=False):
        collection = self.get_collection(collection_name)
        return collection.update_one({'_id': ObjectId(document_id)}, update, upsert=upsert)

    def close(self):
        self.client.close()
    
    def __del__(self):
        self.client.close()