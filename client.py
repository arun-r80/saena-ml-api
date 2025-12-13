from fastapi import FastAPI, Header, HTTPException, Response
from contextlib import asynccontextmanager
from database import db
from openai import OpenAI
from dotenv import load_dotenv
import os, sys
import logging
from typing import Annotated
from classes.classes import ChatHeaderModel, ChatRequestBodyModel, ChatResponseBodyModel


db_collection = None
db_client = None
openai = None
DB_NAME = None
logger = None



#Create lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):
   global db_collection,  client, openai, DB_NAME, logger

   # Create Logger
   logging.basicConfig(
      format="%(asctime)s %(levelname)s %(name)s - %(message)s - App Correlation Id: %(appcorrid)s Conversation Id:%(conversationid)s  %(object)s",
      level=logging.INFO, 
      handlers=[logging.StreamHandler()]
)
   logger = logging.getLogger(__name__)
   logger.info("Logger Initialized",extra=dict(appcorrid=None, object=None, sessionid=None ) )

   try: 
    load_dotenv()
    db_uri= os.environ["DB_CONNECTION_STRING"]
    DB_NAME= os.environ["DB_NAME"]
    COLLECTION_NAME= os.environ["COLLECTION_NAME"]
    
    

    client = await db.get_db_client(uri=db_uri)
    logger.info("DB Client created.", extra=dict(appcorrid=None, object=None,sessionid=None))
    database=client[DB_NAME]
    logger.info("DB Object created: "+ DB_NAME, extra=dict(appcorrid=None, object=None,sessionid=None))
    collection=database[COLLECTION_NAME]
    logger.info("DB Collection object created: " + COLLECTION_NAME, extra=dict(appcorrid=None, object=None,sessionid=None))
    
   except Exception as e: 
      logger.error("Error occured while creating database" + str(e), extra=dict(appcorrid=None, object=None,sessionid=None))
      raise e
   yield
   client.close()


app=FastAPI(lifespan=lifespan)

from pydantic import BaseModel



@app.get("/", status_code=201)
async def root(api_response: Response, headers: Annotated[ChatHeaderModel, Header()] = None, request:ChatRequestBodyModel = None)-> ChatResponseBodyModel:
   global client, DB_NAME, db_collection
   connection_status = False
   
   logger.info("Received Request ", extra=dict(appcorrid= headers.x_appcorrelationid, object=request.model_dump(mode='python')))

   try: 
      response = ChatResponseBodyModel(
      messages=request.message + " Is the response", 
      connection_status= connection_status, 
      db_name=DB_NAME, 
      header_user_name= headers.user_name,
      header_appcorrid = headers.x_appcorrelationid,
      
   )  
      
      return response
   except Exception as e: 
      logger.error("Error creating response: ",  
                   stack_info=True,
                   exc_info=True, 
                   extra=dict(appcorrid= headers.x_appcorrelationid, object=request.model_dump(mode='python')))
      raise HTTPException(status_code=422, detail=str(e))
  
   

@app.post("/getchatresponse")
async def get_char_response(api_response:Response): 
   return

# Create an end point to take request from front end
# May be create a class that will define methods to host LangGraph
# from this endpoint, call that method
# You can then probably send the response back to the requester