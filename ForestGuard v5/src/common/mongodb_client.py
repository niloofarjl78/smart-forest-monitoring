"""
Common MongoDB client utilities.
"""

from pymongo import MongoClient
import json
import os

class MongoDBClient:
    def __init__(self, config_path=None):
        if config_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(script_dir, '..', '..')
            config_path = os.path.join(project_root, 'config', 'config.json')
            
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.connection_string = config["mongodb"]["connection_string"]
        self.database_name = config["mongodb"]["database"]
        self.client = None
        self.db = None
        
    def connect(self):
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            # Test the connection
            self.client.server_info()
            return True
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            return False
    
    def insert_sensor_data(self, data):
        try:
            return self.db.sensor_data.insert_one(data)
        except Exception:
            return None
    
    def get_latest_data(self, limit=50):
        try:
            return list(self.db.sensor_data.find().sort("timestamp", -1).limit(limit))
        except Exception:
            return []
    
    def find_latest(self, collection_name, query={}):
        try:
            if not self.client:
                self.connect()
            collection = self.db[collection_name]
            return collection.find_one(query, sort=[("timestamp", -1)])
        except Exception:
            return None
