#!/usr/bin/env python3
"""
Script to wipe/reset all MongoDB collections
"""
import sys
import os

# Add project root to sys.path for imports
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from src.common.mongodb_client import MongoDBClient

def wipe_mongodb():
    """Wipe all data from MongoDB collections"""
    client = MongoDBClient()
    if not client.connect():
        print("Failed to connect to MongoDB")
        return False
    
    try:
        # Get all collection names
        collections = client.db.list_collection_names()
        print(f"Found collections: {collections}")
        
        # Drop all collections
        for collection_name in collections:
            client.db[collection_name].drop()
            print(f"Dropped collection: {collection_name}")
        
        print("MongoDB wipe completed successfully")
        return True
        
    except Exception as e:
        print(f"Error wiping MongoDB: {e}")
        return False
    finally:
        if client.client:
            client.client.close()

def wipe_sensor_data_only():
    """Wipe only sensor data, keeping other collections"""
    client = MongoDBClient()
    if not client.connect():
        print("Failed to connect to MongoDB")
        return False
    
    try:
        # Delete specific collections
        collections_to_wipe = ['sensor_data', 'alerts', 'devices', 'device_catalog']
        
        for collection_name in collections_to_wipe:
            if collection_name in client.db.list_collection_names():
                result = client.db[collection_name].delete_many({})
                print(f"Deleted {result.deleted_count} documents from {collection_name}")
        
        print("Sensor data wipe completed successfully")
        return True
        
    except Exception as e:
        print(f"Error wiping sensor data: {e}")
        return False
    finally:
        if client.client:
            client.client.close()

if __name__ == "__main__":
    print("MongoDB Data Wiper\n==================")
    if len(sys.argv) > 1:
        if sys.argv[1] == "--sensors-only":
            wipe_sensor_data_only()
        elif sys.argv[1] == "--all":
            print("Performing complete database wipe...")
            wipe_mongodb()
        else:
            print("Unknown argument. Use --sensors-only or --all")
    else:
        print("This will delete ALL data from MongoDB!")
        confirm = input("Type 'yes' to continue: ")
        if confirm.lower() == 'yes':
            wipe_mongodb()
