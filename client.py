from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from utilities.utilities import LogWrapper
from typing import Annotated
from classes.classes import ApiCheckRequestBodyModel, ChatHeaderModel, ChatRequestBodyModel, ChatResponseBodyModel, StateSchema
from graph.graph import GraphFlowWrapper
from utilities.utilities import get_graph_state_from_model_request, get_graph_metadata_from_model_request
from pydantic import BaseModel


db_collection = None
db_client = None
openai = None
DB_NAME = None
logger = None
graph:GraphFlowWrapper = None
logwrapper: LogWrapper = None



#Create lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):
   global graph, logwrapper

   logwrapper = LogWrapper()
   logwrapper.log_info("Logger Initialized")
   

   try: 
      graph = GraphFlowWrapper(logwrapper)
      graph.compile()
   
   except Exception as e: 
      logwrapper.log_exception("Error occured while creating database" + str(e))
      raise e
   yield
   await graph.close()

## Set up CORS Middleware layer for cross-origin requests in local
origins = ["http://localhost:3000", "http://192.168.0.176:3000","https://saena-ml-ui-chat.vercel.app"]


app=FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, 
                    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])





@app.post("/api/formassist", status_code=201)
async def root(api_response: Response, headers: Annotated[ChatHeaderModel, Header()] = None, request:ChatRequestBodyModel = None)-> ChatResponseBodyModel:
   global graph, logwrapper
   connection_status = False
   
   # logger.info("Received Request: " + request.model_dump(mode='python'))
   print(f"Request Object is : {request}")
   print(f"headers: {headers}")
   try: 
      response:StateSchema = await graph.invoke(get_graph_state_from_model_request(request), get_graph_metadata_from_model_request(request, headers))
      model_response:ChatResponseBodyModel = ChatResponseBodyModel(
      messages=response["messages"][-1].content , 
      model_response_id=response["current_conversation_id"],
      header_appcorrid=headers.app_correlation_id
      )
      api_response.status_code = response["api_response_status_code"]  
      
      return model_response
   except Exception as e: 
      logwrapper.error("Error creating response: ",  
                   stack_info=True,
                   exc_info=True, 
                   extra=dict(appcorrid= headers.app_correlation_id, object=request.model_dump(mode='python')))
      raise HTTPException(status_code=422, detail=str(e))
  
   

@app.post("/")
def app_check(message:ApiCheckRequestBodyModel): 
   global graph, logwrapper
   logwrapper.log_info("API called")
   return {"message": message.message}



# Create an end point to take request from front end
# May be create a class that will define methods to host LangGraph
# from this endpoint, call that method
# You can then probably send the response back to the requester