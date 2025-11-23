"""
Module with utility fuctions
"""
from langchain_core.runnables import RunnableConfig

import logging

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
        