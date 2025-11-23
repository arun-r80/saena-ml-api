from typing import TypedDict, Annotated, TypeVar
from pydantic import BaseModel
from enum import Enum
from langgraph.graph.message import add_messages, AnyMessage
from langgraph.graph import StateGraph
from operator import add

class ChatRequestBodyModel(BaseModel):
    previous_conversation_id: str | None = None 
    # The id which is given to llm OpenAI model, for the model to understand previous context messages
    # In short, this id links the conversation for LLM's memory. 
    conversation_id: str | None = None
    # Id to identify a "logical" conversation - ie., a session in which the short term memory (i.e, the state)
    # gets updated. this session id is used to retrieve the short term memory object from database. 
    # In short, this id corresponds to chatbot's memory.
    message: str | None = None
    # Message typed by the user. 

class ChatResponseBodyModel(BaseModel):
   messages: str
   connection_status: bool
   db_name: str
   header_user_name: str
   header_appcorrid: str

class ChatHeaderModel(BaseModel):
    """
    Object providing header values for requests to chat model
    x_Appcorrelationid: GUID value representing each unique request from Front end
    user_name: Abstraction representing user name resolved by Cloud Provider(Azure) based
        based on authentication
    """
    x_appcorrelationid: str | None
    user_name: str | None


class AccountArtifactType(Enum):
    Defect = "Epic"
    Task = "Subtask"
    SubTask = "Subtask"
    Story = "Story"
    Feature = "Feature"
    Request = "Request"
    Bug = "Bug"

class AccountAttributesSchema(BaseModel):
    issue_type: AccountArtifactType
    story_point: int
    summary: str
    description: str

class StateSchema(TypedDict):
    attribute_state: AccountAttributesSchema
    messages: Annotated[list[AnyMessage], add_messages]
    previous_conversation_id: str
    current_conversation_id: str
    response: list

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
role_mapping = {
   "system":"developer", 
   "human": "user" ,
   "ai": "assistant"
}

# Type Variables
GraphRunMetaSchemaT = TypeVar("GraphRunMetaSchemaT", bound=GraphRunMetaSchema)
      




