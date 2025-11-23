"""
define tools for graph node outputs
"""

_01_t_orcgraph_identify_create_usecase = {
    "type": "function", 
    "name": "_01_t_orcgraph_identify_create_usecase", 
    "description": """Tool to be called if the user wants to create an account, as ascertained by 
    intent expressed  by the user in current and previous messages
    """,
    "strict": True,
      "parameters": {
        "type": "object", 
        "properties": {},
        "additionalProperties": False}
}

_01_t_orcgraph_identify_otherscenarios_usecase = {
    "type":"function", 
    "name": "_01_t_orcgraph_identify_otherscenarios_usecase",
    "description": """ Tool to be called, if the user intent as derived from present and past conversations given by the user, 
    that the user does not want to create an account. Tool to be called, when based on user conversations, 
    user intent is not clear or it is difficult to ascertain if the user intent is to create account. 

""", 
    "strict": True, 
    "parameters": {
        "type": "object", 
        "properties": {},
        "additionalProperties": False}
}