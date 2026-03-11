import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(
    os.getenv("MONGO_URI"),
    tlsCAFile=certifi.where(),
)

db = client["adaptive_test"]

questions_collection = db["questions"]
sessions_collection = db["user_sessions"]

# Indexes improve performance
questions_collection.create_index("difficulty")
sessions_collection.create_index("session_id", unique=True)