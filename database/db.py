from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from pymongo.asynchronous.mongo_client import AsyncMongoClient
from pydantic import BaseModel
import asyncio
from logging import Logger
from utilities.utilities import LogWrapper

# define function to create mongodb connection
def get_db_client(uri: str = None,retries: int = 3, delay: float = 1.0):
    
    for i in range(retries): 
        try: 
            client = MongoClient(uri, server_api=ServerApi(version="1", strict=True, deprecation_errors=True))
            return client
        except Exception as e: 
            print(f"Retry: {i+1} - Connect with MongoDB") 
            asyncio.sleep(delay)
    raise RuntimeError(f"MongoDB connects faied after {retries} retries. Aborting Server Startup!")

def get_async_db_client(uri: str,logger: LogWrapper, retries: int = 3, delay: float = 1.0): 
    for i in range(retries): 
        try: 
            async_client = AsyncMongoClient(uri)
            return async_client
        except Exception as e: 
            logger.log_exception(message=f"Connection to MongoDB Failed: {i}",config=None)
            asyncio.sleep(1)
    raise RuntimeError(f"MongoDB connects faied after {retries} retries. Aborting Server Startup!")
            



    
