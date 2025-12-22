"""
Module with utility fuctions
"""
from langchain_core.runnables import RunnableConfig
from classes.classes import UseCaseNames
from graph.messages import context_orcgraph_02_create_artifact_identify_attributelist, context_orcgraph_03b_other_usecase_
from graph.tools import _01_t_orcgraph_identify_create_savings_account_usecase, _01_t_orcgraph_identify_otherscenarios_usecase
import logging
from typing import Dict
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

    def log_info(self, message: str, config:RunnableConfig): 
        appcorrid = None
        conversationid = None
        if config is not None: 
            appcorrid=config["metadata"]["app_correlation_id"]
            conversationid=config["configurable"]["thread_id"]
        message += f"App Correlation Id: {appcorrid} Conversation Id: {conversationid}"
        self.logger.info(message)
        
    
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


