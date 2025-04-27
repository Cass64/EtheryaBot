from pymongo import MongoClient

client = None

def connect_to_mongo(uri):
    global client
    client = MongoClient(uri)
    print("✅ Connecté à MongoDB")

def get_database(name):
    global client
    return client[name]
