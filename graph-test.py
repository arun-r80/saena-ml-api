"""
Test module to test graph wrapper class
"""

from graph.graph import GraphFlowWrapper
from typing import TypeVar
from langchain_core.messages import HumanMessage
from pymongo import database
from pymongo.asynchronous.mongo_client import AsyncMongoClient
from dotenv import load_dotenv
from database import db
import asyncio
import os
import logging
from classes.classes import StateSchema,GraphRunMetaSchema
from pprint import pprint
from classes.utilities import LogWrapper

load_dotenv
 # Create Logger
# logging.basicConfig(
#       format="%(asctime)s %(levelname)s %(name)s - %(message)s - App Correlation Id: %(appcorrid)s Conversation Id:%(conversationid)s  %(object)s",
#       level=logging.INFO, 
#       handlers=[logging.StreamHandler()]
# )
# logger = logging.getLogger("__name__")

#  self.db_collection = collection
#         self.state = None
#         self.stategraph = None
#         self.compiledgraph = None
#         self.mongo_async_client = client
#         self.logger = logger
#         self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# graph_wrapper = GraphFlowWrapper(logger=logger)
# graph_wrapper.compile()
# state = StateSchema(attribute_state=None, messages=[], previous_conversation_id=None, current_conversation_id=None, responses=[])
# config = GraphRunMetaSchema(conversation_id=None, app_correlation_id="arun_1234", user="arun")
# response = await graph_wrapper.invoke(state,config=config )
# print("Response is ", response)

async def get_response():
    graph_wrapper = GraphFlowWrapper(log=LogWrapper())
    graph_wrapper.compile()
    state = StateSchema(attribute_state=None, 
                        messages=[HumanMessage("I want to open an account")], 
                        previous_conversation_id=None, 
                        current_conversation_id=None, 
                        response_code_code=200,
                        responses=[])
    config = GraphRunMetaSchema(conversation_id="arun-21Nov-01", app_correlation_id="arun_1234", user="arun")
    response = await graph_wrapper.invoke(state,config )
   
asyncio.run(get_response())

