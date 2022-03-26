from pymongo import MongoClient, ssl_support
import certifi
import os
from dotenv import load_dotenv
load_dotenv()

DB_URI = os.getenv("DB_URI")
client = MongoClient(DB_URI,tlsCAFile=certifi.where())
db=client['investing']
# db= client
