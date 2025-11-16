# Saena ML API - Backend Framework implementing Graph

## State Schema 
The defined state schema is critical and unique for an implementation pathway of a graph. State Schema for this graph contains the following key attributes: \
class StateSchema(TypedDict): \
    attribute_state: AccountAttributesSchema \
    - Schema object representing short term memory between individual message turns ( ie., between different graph implementations). 
    Stored in MongoDB instance,and it indexed by a session id
    session_id: str \
    - UUID representing one conversation thread with the user \
    app_correlation_id: str \
    - App Correlation ID - Corresponds to one specific turn or message provided by the user \
    user: str \
    - Name of the sure as identified by IdP, specifically transferred in header request to App Service \
    messages: Annotated[list, add] \
    - Context and User messages for one  execution of graph \
    previous_conversation_id: str \
    - Previous conversation id to be passed to OpenAI. An alternative to storing individual user/system context messages in a seperate store \
    current_conversation_id: str \
    - Current conversation id returned by OpenAI, in each individual invoking, invoked during each individual execution of the graph. \ 
    For example, if the user messages that "I want to open an account", then the graph is invoked with this individual message as input. 
    As the graph passes through individual nodes, LLMs are called as intermediate step, and each LLM invoking returns conversation id that is stored in the state. \
    response: list \
    - Stores response object returned by LLM to be used by conditional edges predominantly, in subsequent steps. \
