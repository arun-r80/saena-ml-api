from typing import TypedDict, Annotated
from pydantic import BaseModel
from enum import Enum
from langgraph.graph.message import add_messages

class ChatRequestBodyModel(BaseModel):
    previous_conversation_id: str | None = None 
    # The id which is given to llm OpenAI model, for the model to understand previous context messages
    # In short, this id links the conversation for LLM's memory. 
    session_id: str | None = None
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


class JiraArtifactType(Enum):
    Defect = "Epic"
    Task = "Subtask"
    SubTask = "Subtask"
    Story = "Story"
    Feature = "Feature"
    Request = "Request"
    Bug = "Bug"

class JiraAttributesSchema(BaseModel):
    issue_type: JiraArtifactType
    story_point: int
    summary: str
    description: str

class State(TypedDict):
    attribute_state: JiraAttributesSchema
    messages: Annotated[list, add_messages]
    previous_conversation_id: str | None
    current_conversation_id: str | None
    session_id: str | None



class AppConfig:
  MODEL: str = "gpt-4o-mini"
  USER: str = "ARUN"

class ThreadConfig(BaseModel):
  thread_id: str
  checkpoint_id: str = None
  recursion_limit: int = 100





