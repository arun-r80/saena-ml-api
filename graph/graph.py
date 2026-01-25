"""
Implemntation class that encapsulates graph flow, building an interface that effectively exposes graph initialization, 
compilation and invoking methods. 
"""
import sys, os, json
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.types import StateSnapshot
from typing import Iterator
from langgraph.checkpoint.memory import InMemorySaver
from pymongo.asynchronous.mongo_client import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.client_session import AsyncClientSession
from typing import Annotated, Sequence
from classes.classes import BaseGraph, SavingsAccountAttributesSchema, StateSchema,AppConfig,ThreadConfig, role_mapping, GraphRunMetaSchema, GraphRunMetaSchemaT, UseCaseNames,_02_tool_content_mapping_
from utilities.utilities import LogWrapper
from pymongo.collection import Collection
from openai import OpenAI, Client
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, AnyMessage, ToolMessage
from langgraph.graph.state import CompiledStateGraph
from graph.messages import context_orcgraph_01_identifycreateuse,context_03a_node_validate_attributelist_, context_orcgraph_03b_other_usecase_,structuredoutput_orcgraph_02_attributelist
from graph.tools import _01_t_orcgraph_identify_create_savings_account_usecase, _01_t_orcgraph_identify_otherscenarios_usecase, tool_mapping
from langgraph.typing import InputT
from langchain_core.runnables import RunnableConfig
from logging import Logger
from database.db import get_async_db_client
from openai.types.responses import Response
from fastapi import status
from pydantic import ValidationError
from utilities.utilities import use_case_mapping
from pprint import pprint
from utilities.utilities import get_runnable_config




class GraphFlowWrapper[T: StateSchema](BaseGraph):
    """"
    Wrapper class that encapsultates graph interface methods
    """
    
    db_collection: AsyncCollection
    db: AsyncDatabase
    mongo_async_client: AsyncMongoClient
    stategraph: StateGraph
    compiledgraph: CompiledStateGraph
    client: Client
    log: LogWrapper
    def __init__(self, log: LogWrapper):
        """
        Initialize graph flow wrapper
        """
        load_dotenv()
        db_uri= os.environ["DB_CONNECTION_STRING"]
        DB_NAME= os.environ["DB_NAME"]
        COLLECTION_NAME= os.environ["COLLECTION_NAME"]

        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.log = log
        self.stategraph = None
        self.compiledgraph = None
        
        # Initialize Asynchronous connection options
        try: 
            self.mongo_async_client = get_async_db_client(db_uri, self.log.logger)
            self.db = AsyncDatabase(self.mongo_async_client, DB_NAME)
            self.db_collection = AsyncCollection(self.db, COLLECTION_NAME)
            self.log.log_info(message="GraphWrapper: DB connection established")
        except Exception as e: 
            self.log.log_exception(message="Error during initialization of Database", config=None)
            raise e
        self.log.log_info(message="GraphWrapper: Graph object compiled")

    def _01a_node_add_identfyusecase_sysprompt(self, s: StateSchema, config: RunnableConfig) -> StateSchema:
        """
        Node to add system context prompt to identify use case. This step is an intermediary 
        to add necessary context to state, for subsquent call to identify use case based on user message. 
        Args:
        self - instance of current class
        s - state object for the graph
        """
        return {"messages":SystemMessage(context_orcgraph_01_identifycreateuse)}
    
    async def _01_node_identify_usecase(self, s: StateSchema, config: RunnableConfig)->StateSchema:
        """
        Node to identify intended use case of the user, based on user input and system context prompt given in earlier
        node. 
        """
        # Create input list
        input_list = [{"role": role_mapping[_d.type],"content": _d.content } for _d in s["messages"]]
        print(f"Input List: {input_list}")
        # get response
        kwargs = {}
        if s["previous_conversation_id"] != '': 
            kwargs["previous_response_id"] = s["previous_conversation_id"]
        try: 
            response = self.client.responses.create(
                model=AppConfig.MODEL, 
                input=input_list, 
                user=config["metadata"]["user"],
                tools=[_01_t_orcgraph_identify_create_savings_account_usecase, _01_t_orcgraph_identify_otherscenarios_usecase ], 
                **kwargs
            )
        #TODO - Handle api errors as in https://platform.openai.com/docs/guides/error-codes#api-errors
        #TODO - Handle OpenAI call as part of method rather than calls from individual nodes
        except KeyError as ke: 
            pass
        return {"current_conversation_id":response.id,
                "response": response
                }
    async def _02_node_branch_for_usecase(self, state: StateSchema ) -> str: 
        """
        Conditional edge that routes graph flow to appropriate use case, or to failure scenario
        """
        #Check for refusal in message

        for output in  state["response"].output: 
            if output.type == "message":
                for c in output.content: 
                    if c.type == 'refusal': 
                        return({
                            "messages":AIMessage("There was a refusal to get your response:  "  + c.refusal),
                            "api_response_status_code": status.HTTP_409_CONFLICT,
                            
                            "usecase_conditional_status":"Refusal"})
                    if c.type == "output_text":
                        return({
                            "messages":AIMessage(c.text),
                            "api_response_status_code": status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
                            "usecase_conditional_status":"Other Message"})
                        
            if output.type == "function_call":
                
                    return {
                            "usecase_conditional_status":output.name,
                            "messages": ToolMessage(_02_tool_content_mapping_[output.name], tool_call_id=output.call_id)
                            }
                

    async def _03b_node_other_usecase_(self, state:StateSchema, config:RunnableConfig)-> StateSchema:
        """"
        This node is to provide an output that the use case is different from creating an account. 
        """ 
        llm_response = self.client.responses.create(
            model=AppConfig.MODEL, 
            input=[{
                "call_id":state["messages"][-1].tool_call_id, 
                "type":"function_call_output",
                "output":use_case_mapping[state["usecase_conditional_status"]]

            }],
            # tools=[tool_mapping[state["usecase_conditional_status"]]],
            previous_response_id=state["current_conversation_id"], 
            user=config["metadata"]["user"],
            max_output_tokens=80
        )
        #TODO - Handle OpenAI call as part of method rather than calls from individual nodes
        llm_response_text:str = None
        for output in llm_response.output:
            for c in output.content:
                if c.type == "refusal":
                    return(
                        {
                            "messages":AIMessage("There was a refusal to get your response:  "  + c.refusal),
                            "api_response_status_code": status.HTTP_409_CONFLICT,
                            "current_conversation_id":llm_response.id, 
                            "usecase_conditional_status":"Refusal"}
                    )
                llm_response_text =c.text

        return({"messages": AIMessage(llm_response_text),
                "usecase_conditional_status":"process" ,
                "current_conversation_id": llm_response.id})

    async def _03a_node_identify_attribute_list(self, state:StateSchema, config:RunnableConfig) -> StateSchema:
        """
        This function identifies list of attributes provided by the user in the input message, and also identifies the associated
        values for the input through structured output.
        
        :param self: self object
        :param state: graph state, passed as input to this node
        :type state: StateSchema
        :return: updated state schema
        :rtype: StateSchema
        """
        
        
        # TODO Handle errors as given in https://platform.openai.com/docs/guides/error-codes#api-errors
        llm_response = self.client.responses.create(
            model=AppConfig.MODEL, 
            input=[{
                "call_id":state["messages"][-1].tool_call_id, 
                # "id":id,
                "type":"function_call_output",
                "output":use_case_mapping[state["usecase_conditional_status"]]

            }],
            # tools=[tool_mapping[state["usecase_conditional_status"]]],
            text=structuredoutput_orcgraph_02_attributelist,
            user=config["metadata"]["user"],
            previous_response_id=state["current_conversation_id"]
        )

        llm_response_model:str
        for output in [o for o in llm_response.output if o.type == "message"]: 
            for c in output.content:  
                if c.type == "refusal":
                    return {"usecase_conditional_status":"Refusal",
                            "messages": AIMessage(c.refusal), 
                            "api_response_status_code": status.HTTP_409_CONFLICT, 
                            "current_conversation_id":llm_response.id
                              }
                # get string-converted attribute dict object
                attribute_text= json.loads(c.text)
                attribute_list= attribute_text['attribute_list']
                llm_response_model = {key:value for key, value in zip([k["attribute_name"] for k in attribute_list], [v["attribute_value"] for v in attribute_list]) } 
                
        tmp = state["attribute_state"] if state["attribute_state"] else dict()
        tmp.update(llm_response_model)
        return({
            "attribute_state": tmp,
            "usecase_conditional_status":"Process", 
            "current_conversation_id": llm_response.id, 
            "response":llm_response
        })





    async def _03a_node_validate_attributelist_(self, state: StateSchema)-> StateSchema:
        """
        NOde to provide validation information between current attribute values and attribute schema, which will 
        be injected to conversation context to evoke right user response from the model.
        """
        current_attribute_values = state["attribute_state"]
        if current_attribute_values == None: 
            return{"messages":SystemMessage(context_03a_node_validate_attributelist_ + "The user has not provided value for any of the attributes till now")}
        try: 
            SavingsAccountAttributesSchema.model_validate(current_attribute_values)
        except ValidationError as ve:
            return({"messages":SystemMessage(context_03a_node_validate_attributelist_ + str(ve)),
                    "usecase_conditional_status":"validation_error"}
                    )
        return({"usecase_conditional_status":"create_attribute_success"})
            
    async def _04a_node_validation_failure_response_(self, state:StateSchema, config:RunnableConfig)-> StateSchema:
        """
        Return a message to user that there are validation error messages in creation of an account
        """
        llm_response = await self.call_openai_llm(
                message=state["messages"][-1],
                state=state, 
                user=config["metadata"]["user"]

        )
        llm_response_text:str = ""
        for output in [o  for o in llm_response.output if o.type == "message"] :
            for c in [content for content in output.content if content.type == 'output_text']:
                llm_response_text = c.text 
                break

        return ({
            "current_conversation_id":llm_response.id,
            "messages":AIMessage(llm_response_text), 
            "response": llm_response

        })


    def _04b_node_create_attribute_success(self, state:StateSchema)->StateSchema:
        """
        Node to provide success message for creation of a savings bank account to the user
        """
        successful_creation_message = f"""
            Savings Bank Account created successfully with following attributes: 
            {"\n".join([f"{d}:{state["attribute_state"][d]}" for d in state["attribute_state"]])}
            """
        return{
            "messages":AIMessage(successful_creation_message)
        }
    

    async def call_openai_llm(self,message:AnyMessage=None, state: StateSchema=None, **kwargs)-> Response:
        """
        Utility function to make calls to LLM, which reduces need for additional nodes and keeps overall graph flow simpler to comprehend
        """
        #TODO - Handle Python OpenAI errors as given in https://platform.openai.com/docs/guides/error-codes#api-errors
        return self.client.responses.create(
            previous_response_id=state["current_conversation_id"], 
            model=AppConfig.MODEL,
            input=[dict(role=role_mapping[message.type], content=message.content)], 
            **kwargs
        )
    
    
    
    def compile(self) -> bool:
        """
        Method to initialize, compile and assign compiled state graph as attribute in graph wrapper object
        """
        try: 
            
            checkpointer = InMemorySaver()
            graph_builder = StateGraph(StateSchema)
            # Add Graph Nodes
            graph_builder.add_node("_get_short_term_memory", self._preprocess_get_short_term_memory_for_conversationid)
            graph_builder.add_node("01a_add_usecase_context",self._01a_node_add_identfyusecase_sysprompt )
            graph_builder.add_node("_01_process_usecase_identification", self._01_node_identify_usecase)
            graph_builder.add_node("_update_short_term_memory", self._postprocess_update_short_term_memory_for_conversation)
            graph_builder.add_node("_02_branch_for_usecase", self._02_node_branch_for_usecase)
            graph_builder.add_node("_03b_node_other_usecase_", self._03b_node_other_usecase_)
            graph_builder.add_node('_03a_node_identify_attribute_list', self._03a_node_identify_attribute_list)
            graph_builder.add_node("_03a_node_validate_attributelist_", self._03a_node_validate_attributelist_)
            graph_builder.add_node("_04a_node_validation_failure_response_", self._04a_node_validation_failure_response_)
            graph_builder.add_node("_04b_node_create_attribute_success", self._04b_node_create_attribute_success)
            # Add Graph Edges
            graph_builder.add_edge(START, "_get_short_term_memory")
            graph_builder.add_edge("_get_short_term_memory", "01a_add_usecase_context")
            graph_builder.add_edge("01a_add_usecase_context","_01_process_usecase_identification" )
            graph_builder.add_edge("_01_process_usecase_identification","_02_branch_for_usecase")
            graph_builder.add_conditional_edges("_02_branch_for_usecase", 
                                                lambda state:state["usecase_conditional_status"],
                                                {
                                                    "Refusal": END,
                                                    "Other Message": END,
                                                    "_01_t_orcgraph_identify_create_savings_account_usecase":"_03a_node_identify_attribute_list",
                                                    "_01_t_orcgraph_identify_otherscenarios_usecase":"_03b_node_other_usecase_"
                                                }
                                                )
            graph_builder.add_conditional_edges("_03a_node_identify_attribute_list", 
                                                lambda state: state["usecase_conditional_status"], 
                                                {
                                                    "Refusal": END,
                                                    "Process": "_03a_node_validate_attributelist_"
                                                }
                                                
                                                )
            graph_builder.add_conditional_edges("_03a_node_validate_attributelist_", 
                                                lambda state: state["usecase_conditional_status"], 
                                                {
                                                    "validation_error":"_04a_node_validation_failure_response_", 
                                                    "create_attribute_success":"_04b_node_create_attribute_success"
                                                }
                
            )
            graph_builder.add_edge("_03b_node_other_usecase_", END)
            graph_builder.add_edge("_04a_node_validation_failure_response_" ,"_update_short_term_memory" )
            graph_builder.add_edge("_04b_node_create_attribute_success" ,"_update_short_term_memory" )
            graph_builder.add_edge("_update_short_term_memory", END)

            self.compiledgraph= graph_builder.compile(checkpointer=checkpointer)
            self.log.log_info(message="GraphWrapper: Graph Compiled")
        except Exception as e: 
            self.log.log_exception(message="Exception occured during creation of graph" + str(e), config=None)
            raise e
        
    async def close(self):
        """
        Close DB collection during uvicorn server shutdown
        
        :param self: Description
        :return: Description
        :rtype: Any
        """    
        try: 
            await self.mongo_async_client.close()
            self.log.log_info("DB connection closed successfully")
        except Exception as e:
            self.log.log_exception("Exception raised during closing DB Connection")

    def get_state_history(self, config:RunnableConfig) -> Iterator[StateSnapshot]:
        """
        Provide checkpointer list for compiled graph
        """
        return self.compiledgraph.get_state_history(config)
    
   

    async def _preprocess_get_short_term_memory_for_conversationid(self,state: StateSchema,  config: RunnableConfig) -> StateSchema: 
            """
            Utility method to get state for a particular session
            """
            try:
                self.log.log_info("Retrieving short term meomry for session id", config )
                
                async with self.mongo_async_client.start_session(causal_consistency=True) as session:
                    response = await  self.db_collection.find_one(
                            filter=dict(conversation_id=config["metadata"]["conversation_id"], 
                                use_case=UseCaseNames.create_savings_account.value), 
                            projection={
                                '_id':False, 
                                "use_case":False,
                                "conversation_id":False
                            },
                            session=session)
                    return {"attribute_state": response}
            except Exception as e: 
                self.log.log_exception(message="Error during retrieval of short term memory for session id " + str(e), config=config)
                                  
                return state        
    
    async def _postprocess_update_short_term_memory_for_conversation(self,state:StateSchema,  config:RunnableConfig) -> StateSchema:
        """
        Utility function to store session data into short term memory
        """
        try:                 
            self.log.log_info("Update/Upsert State information to short-term memory ", config )
            
            async  with self.mongo_async_client.start_session( causal_consistency=True) as session: 
                if state["attribute_state"] is not None: 
                    match state["usecase_conditional_status"]:
                        case "validation_error":
                            update_record = await self.db_collection.update_one(dict(conversation_id=config["metadata"]["conversation_id"],use_case=UseCaseNames.create_savings_account.value),
                                {"$set": {key:state['attribute_state'][key] for key in state["attribute_state"].keys()}},
                                upsert=True, 
                                session=session) 
                            update_message = f"Update Record: Updated savings account creation attirbutes.  No of documents matched: {update_record.matched_count}  Did Upsert Happen:{update_record.did_upsert} \
                                No of documents modified:{update_record.modified_count}"
                            self.log.log_info( update_message, config)
                        case "create_attribute_success":
                            update_record = await self.db_collection.update_one(dict(conversation_id=config["metadata"]["conversation_id"],use_case=UseCaseNames.create_savings_account.value),
                                {"$unset": {key:"" for key in state["attribute_state"].keys()}},
                                upsert=True, 
                                session=session) 
                            update_message = f"Update Record: Purged savings account attributes post account creation.   No of documents matched: {update_record.matched_count}  Did Upsert Happen:{update_record.did_upsert} \
                                No of documents modified:{update_record.modified_count}"
                            self.log.log_info( update_message, config)
                return state
                
        except Exception as e: 
            self.log.log_exception(message="Error during updating short term memory " + str(e), config=config)
            return state

    

    async def invoke(self , input: StateSchema, graph_config: RunnableConfig | GraphRunMetaSchemaT )->StateSchema:
        """
            Invoke graph to get final response
        """ 
        config=get_runnable_config(graph_config)
        try:
            response = await self.compiledgraph.ainvoke(input=input, config=config)
        finally:
            # for h in self.compiledgraph.get_state_history(config):
            #     pprint(h.values)
            #     print("=========================================================================================")
            pass
                
                
        
        return response



    


