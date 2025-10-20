from fastapi import FastAPI, Header
from contextlib import asynccontextmanager
from database import db
from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import Annotated


db_collection = None
db_client = None
openai = None
DB_NAME = None

#Create lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):
   global db_collection,  client, openai, DB_NAME
   try: 
    load_dotenv()
    db_uri= os.environ["DB_CONNECTION_STRING"]
    DB_NAME= os.environ["DB_NAME"]
    COLLECTION_NAME= os.environ["COLLECTION_NAME"]
    OPENAI_API_KEY=os.environ["OPENAI_API_KEY"]

    client = await db.get_db_client(uri=db_uri)
    print("DB Client created.")
    database=client[DB_NAME]
    print("DB Object created: ", DB_NAME)
    collection=database[COLLECTION_NAME]
    print("DB Collection object created: ", COLLECTION_NAME)
    openai = OpenAI(api_key=OPENAI_API_KEY)
    print("Open AI Client created")
   except Exception as e: 
      print("Error occured while creating database", e)
      raise e
   yield
   client.close()


app=FastAPI(lifespan=lifespan)

from pydantic import BaseModel

class ResponseDummy(BaseModel):
   messages: str
   connection_status: bool
   db_name: str
   header_name: str

@app.get("/")
async def root(user_name: Annotated[str | None, Header()] = None)-> ResponseDummy:
    global client, DB_NAME, db_collection
    connection_status = False
    

    response = ResponseDummy(
      messages="Hello, World!", 
      connection_status= connection_status, 
      db_name=DB_NAME, 
      header_name= user_name
   )
   
    return response

@app.post("/getchatresponse")
async def get_char_response(): 
   return

# Create an end point to take request from front end
# May be create a class that will define methods to host LangGraph
# from this endpoint, call that method
# You can then probably send the response back to the requester