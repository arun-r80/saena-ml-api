"""
Module with utility fuctions
"""
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
from classes.classes import ChatHeaderModel, UseCaseNames
from graph.messages import context_orcgraph_02_create_artifact_identify_attributelist, context_orcgraph_03b_other_usecase_
from graph.tools import _01_t_orcgraph_identify_create_savings_account_usecase, _01_t_orcgraph_identify_otherscenarios_usecase
import logging
from typing import Dict
from classes.classes import GraphRunMetaSchema, ChatRequestBodyModel, StateSchema
from fastapi import status
def log_info(logger, message: str, config:RunnableConfig, object=None): 
    logger.info(message,
                exc_info=False, 
                extra=dict(appcorrid=config["metadata"]["app_correlation_id"], conversationid=config["configurable"]["thread_id"], object=object)
                                  )
    
class LogWrapper: 


    """
    Utility class for logging functionality
    """
    
    logger: logging.Logger
    def __init__(self):
        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(name)s - %(message)s",# - App Correlation Id: %(appcorrid)s Conversation Id:%(conversationid)s  %(object)s",
            level=logging.INFO, 
            handlers=[logging.StreamHandler()]
)
        self.logger = logging.getLogger(__name__)

    def log_info(self, message: str, config:RunnableConfig = None): 
        
        if config is not None: 
            appcorrid=config["metadata"]["app_correlation_id"]
            conversationid=config["configurable"]["thread_id"]
            message += f"App Correlation Id: {appcorrid} Conversation Id: {conversationid}"
        self.logger.info(message)

    def error(self, message:str = None, **kwargs):
         """
        A simple wrapper on logger.error 
         
         :param self: Logwrapper object
         :param message: Exception message to be logged
         :type message: str
         :param kwargs: Other key word arguments
         """
         self.logger.error(message, **kwargs)
        
    
    def log_exception(self, message: str = None, config:RunnableConfig | None = None, object=None):
        appcorrid = None
        conversationid = None
        if config is not None: 
            appcorrid=config["metadata"]["app_correlation_id"]
            conversationid=config["configurable"]["thread_id"]
        message += f"App Correlation Id: {appcorrid} Conversation Id: {conversationid}"
        self.logger.exception(message,  exc_info=True, stack_info=True, 
                                  extra=dict(appcorrid=appcorrid, conversationid=conversationid, object=object)
                                  )
# use_case_mapping is a dictonariy to map tool name returned by model to corresponding context message to be passed 
# to model as response to this tool call, in subsequent nodes. 
use_case_mapping = dict(
    _01_t_orcgraph_identify_create_savings_account_usecase= context_orcgraph_02_create_artifact_identify_attributelist,
    _01_t_orcgraph_identify_otherscenarios_usecase= context_orcgraph_03b_other_usecase_
)    
# tool_mapping maps a tool name to corresponding tool to be passed as function call output to the model, in subsequent
# steps to close tool call. 


def get_runnable_config(config: GraphRunMetaSchema) -> RunnableConfig: 
        """
        return runnable config from graph metadata schema
        """

        return RunnableConfig(configurable=dict(thread_id=config.app_correlation_id), 
                                        metadata=dict(app_correlation_id=config.app_correlation_id, user=config.user,conversation_id=config.conversation_id),
                                        recursion_limit=100)


def get_graph_metadata_from_model_request(request: ChatRequestBodyModel, headers: ChatHeaderModel)-> GraphRunMetaSchema:
     """
     Utility function to return Run Metadata Schema object from request sent to model
     
     :param request: Request sent to model as request object to chat api
     :type request: ChatRequestBodyModel
     :return: Metadata schema for graph object
     :rtype: GraphRunMetaSchema
     """
     return GraphRunMetaSchema(conversation_id=request.conversation_id, 
                               app_correlation_id=headers.app_correlation_id, 
                               user = headers.user_name)

def get_graph_state_from_model_request(request:ChatRequestBodyModel )->StateSchema:
     """
     Get graph state from model request
     
     :param request: Model request object
     :type request: ChatRequestBodyModel
     :return: state object conforming to StateSchema
     :rtype: StateSchema
     """
     return(StateSchema(
          attribute_state={}, 
          messages=HumanMessage(request.message), 
          previous_conversation_id=request.previous_response_id, 
          current_conversation_id="", 
          api_response_status_code=status.HTTP_201_CREATED, 
          response=None, 
          usecase_conditional_status=None, 
          error_message=""


     ))