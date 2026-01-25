from typing import TypedDict, Annotated, TypeVar
from pydantic import BaseModel, Field
from enum import Enum
from langgraph.graph.message import add_messages, AnyMessage
from langgraph.graph import StateGraph
from operator import add
from openai.types.responses import Response
from fastapi import status

class ApiCheckRequestBodyModel(BaseModel):
   message: str

class ChatRequestBodyModel(BaseModel):
    previous_response_id: str | None = None 
    # The id which is given to llm OpenAI model, for the model to understand previous context messages
    # In short, this id links the conversation for LLM's memory. If populated, this id will correspond to 
    # id attribute of Responses object, returned by model during last invocation in graph execution. 
    conversation_id: str | None = None
    # Id to identify a "logical" conversation - ie., a session in which the short term memory (i.e, the state)
    # gets updated. this session id is used to retrieve the short term memory object from database. 
    # In short, this id corresponds to chatbot's memory.
    message: str | None = None
    # Message typed by the user. 
    user_name: str | None = "test"
    # User name interacting with the model
    app_correlation_id: str | None = None
    # Unique identifier for each invocation of graph from front-end application or any other consumer. 



class ChatResponseBodyModel(BaseModel):
   messages: str 
   # Message response by the model
   model_response_id: str
   # UUID that represent the id parameter in Responses object retruned by OpenAI Responses Create API call. 
   # This id is needed to preserve previous conversation context, without need to store all conversations. 
   header_appcorrid: str
   # UUID that represent this run(or invoking of model by user with a message)

class ChatHeaderModel(BaseModel):
    """
    Object providing header values for requests to chat model
    x_Appcorrelationid: GUID value representing each unique request from Front end
    user_name: Abstraction representing user name resolved by Cloud Provider(Azure) based
        based on authentication
    """
    user_name: str | None = "test"
    # User name interacting with the model
    app_correlation_id: str | None = None
    # Unique identifier for each invocation of graph from front-end application or any other consumer. 


class SavingsAccountType(Enum):  # AccountArtifactType
    everyday = "every day savings"
    savings = "savings"
    checking = "checking"

class UseCaseNames(Enum):
   ":: Schema for supported use cased by the chatbot. Update the Schema for onboarding new usecase::"
   create_savings_account = "create savings account"
   other_usecase = "other use case"

class SavingsAccountAttributesSchema(BaseModel):
    account_type: SavingsAccountType
    account_holder_name: str
    account_limit: int = Field(gt=0)
    address: str
    

class StateSchema(TypedDict):
    attribute_state: dict
    messages: Annotated[list[AnyMessage], add_messages]
    previous_conversation_id: str
    current_conversation_id: str
    usecase_conditional_status: str
    api_response_status_code: int
    response: Response
    error_message: str

class AppConfig:
  MODEL: str = "gpt-4o-mini"

class GraphRunMetaSchema(BaseModel):
    """
    Contains Schema for metadata, which provides config values for runnable config and other user meta data. 
    """
    conversation_id: str | None
    # UUID representing one conversation thread with the user
    app_correlation_id: str | None
    # App Correlation ID - Corresponds to one specific turn or message provided by the user
    user: str
    # Name of the sure as identified by IdP, specifically transferred in header request to App Service

class ThreadConfig(BaseModel):
  """
  Contains RunnableConfig details for each invocation/run of the graph
  """
  thread_id: str
  checkpoint_id: str = None
  recursion_limit: int = 100

class BaseGraph[state: StateSchema ]:
   """
   Interface class for Graph flow
   """
   def __init__(self):
      pass
   
   def compile(self):
      """
      Compile graph and initialize compiled graph object. 
      """
      return
   
   def invoke(self, s: state) -> state:
      """
      Invoke graph and return updated state

      """
      updates: state 
      return updates
   
# Role mapping dict, with values as open ai role types and keys as LangChain message types
role_mapping:dict = {
   "system":"developer", 
   "human": "user" ,
   "ai": "assistant", 
   "tool":"tool"
}

_02_tool_content_mapping_ = {
   "_01_t_orcgraph_identify_create_savings_account_usecase": "The use case selected by user is create bank account",
   "_01_t_orcgraph_identify_otherscenarios_usecase": "The user has selected a different use case or has provided a different message"
}

# Type Variables
GraphRunMetaSchemaT = TypeVar("GraphRunMetaSchemaT", bound=GraphRunMetaSchema)
      




