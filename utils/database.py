from pymongo import MongoClient

client = None

def connect_to_mongo(MONGO_URI):
    global client
    client = MongoClient(MONGO_URI)
    print("✅ Connecté à MongoDB")

def get_database(name):
    global client
    return client[name]
