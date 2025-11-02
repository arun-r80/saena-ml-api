from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from pydantic import BaseModel
import asyncio

# define function to create mongodb connection
async def get_db_client(uri: str = None,retries: int = 3, delay: float = 1.0):
    
    for i in range(retries): 
        try: 
            client = MongoClient(uri, server_api=ServerApi(version="1", strict=True, deprecation_errors=True))
            return client
        except Exception as e: 
            print(f"Retry: {i+1} - Connect with MongoDB") 
            asyncio.sleep(delay)
    raise RuntimeError(f"MongoDB connects faied after {retries} retries. Aborting Server Startup!")



    
