Saena ML API - Backend Framework implementing Graph

State Schema: 
The defined state schema is critical and unique for an implementation pathway of a graph. State Schema for this graph contains the following key attributes: 
class StateSchema(TypedDict):
    attribute_state: AccountAttributesSchema
    messages: Annotated[list, add]
    previous_conversation_id: str
    current_conversation_id: str
    session_id: str
    # UUID representing one conversation thread with the user
    app_correlation_id: str
    # App Correlation ID - Corresponds to one specific turn or message provided by the user
    user: str
    # Name of the sure as identified by IdP, specifically transferred in header request to App Service
    response: list
