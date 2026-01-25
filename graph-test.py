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

from utilities.utilities import LogWrapper
from pprint import pprint

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
response=None





async def get_response():
    global response
    graph_wrapper = GraphFlowWrapper(log=LogWrapper())
    graph_wrapper.compile()
    # state = StateSchema(attribute_state={}, 
    #                     messages=[HumanMessage("I want to open an account")], 
    #                     previous_conversation_id=None, 
    #                     current_conversation_id=None, 
    #                     usecase_conditional_status=None,
    #                     api_response_status_code=200,
    #                     response=None)
    # state = StateSchema(attribute_state={}, 
    #                     messages=[HumanMessage("Account Holder name is Arun Ramamurthy")], 
    #                     previous_conversation_id="resp_0f3f010259bbed3c006948c3c1fdd481a1a88fd3de1c78aa60", 
    #                     current_conversation_id=None, 
    #                     usecase_conditional_status=None,
    #                     api_response_status_code=200,
    #                     response=None)
    # state = StateSchema(attribute_state={}, 
    #                     messages=[HumanMessage("Address is  Westmead, NSW")], 
    #                     previous_conversation_id="resp_0f3f010259bbed3c006948c3feaee881a1965223706460a3d8", 
    #                     current_conversation_id=None, 
    #                     usecase_conditional_status=None,
    #                     api_response_status_code=200,
    #                     response=None)
    # state = StateSchema(attribute_state={}, 
    #                     messages=[HumanMessage("Account type is savings and limit is 5000")], 
    #                     previous_conversation_id="resp_0f3f010259bbed3c006948c468234481a1b8f787810a3f8a5c", 
    #                     current_conversation_id=None, 
    #                     usecase_conditional_status=None,
    #                     api_response_status_code=200,
    #                     response=None)
    # state = StateSchema(attribute_state={}, 
    #                     messages=[HumanMessage("Address is  Westmead, NSW")], 
    #                     previous_conversation_id="resp_0bfd4ef2c8582701006948addb2e488193a4256d2ad505ba78", 
    #                     current_conversation_id=None, 
    #                     usecase_conditional_status=None,
    #                     api_response_status_code=200,
    #                     response=None)
    # state = StateSchema(attribute_state={}, 
    #                     messages=[HumanMessage("asdf")], 
    #                     previous_conversation_id="resp_0bfd4ef2c8582701006948aef53d348193b0c4030a20c0a769", 
    #                     current_conversation_id=None, 
    #                     usecase_conditional_status=None,
    #                     api_response_status_code=200,
    #                     response=None)
    # state = StateSchema(attribute_state={}, 
    #                     messages=[HumanMessage("Account Limit is 5000")], 
    #                     previous_conversation_id="resp_0bfd4ef2c8582701006948b0cdac148193a4aa82d3e2afe662", 
    #                     current_conversation_id=None, 
    #                     usecase_conditional_status=None,
    #                     api_response_status_code=200,
    #                     response=None)
    # state = StateSchema(attribute_state={}, 
    #                     messages=[HumanMessage("Hi")], 
    #                     previous_conversation_id="resp_0bfd4ef2c8582701006948ba2d05888193932cf9df8eb44848", 
    #                     current_conversation_id=None, 
    #                     usecase_conditional_status=None,
    #                     api_response_status_code=200,
    #                     response=None)
    config = GraphRunMetaSchema(conversation_id="arun-22Dec-01", app_correlation_id="arun_1234", user="arun")
    try: 
        response = await graph_wrapper.invoke(state,config )
    except Exception as e: 
        for h in graph_wrapper.get_state_history(config):
            pprint(vars(h))
    print("Response from model: ", response["messages"][-1].content)
    print("Respoinse Id: ", response["current_conversation_id"])
asyncio.run(get_response())

