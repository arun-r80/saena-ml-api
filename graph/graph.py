"""
Implemntation class that encapsulates graph flow, building an interface that effectively exposes graph initialization, 
compilation and invoking methods. 
"""
import sys, os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from pymongo.asynchronous.mongo_client import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.client_session import AsyncClientSession
from typing import Annotated
from classes.classes import BaseGraph, AccountAttributesSchema, StateSchema,AppConfig,ThreadConfig, role_mapping, GraphRunMetaSchema, GraphRunMetaSchemaT
from classes.utilities import LogWrapper
from pymongo.collection import Collection
from openai import OpenAI, Client
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph.state import CompiledStateGraph
from graph.messages import context_orcgraph_01_identifycreateuse
from graph.tools import _01_t_orcgraph_identify_create_usecase, _01_t_orcgraph_identify_otherscenarios_usecase
from langgraph.typing import InputT
from langchain_core.runnables import RunnableConfig
from logging import Logger
from database.db import get_async_db_client
from openai.types.responses import Response




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
        
        # Initialize Asynchronous connectino options
        try: 
            
            self.mongo_async_client = get_async_db_client(db_uri, self.log.logger)
            self.db = AsyncDatabase(self.mongo_async_client, DB_NAME)
            self.db_collection = AsyncCollection(self.db, COLLECTION_NAME)
        except Exception as e: 
            self.log.log_exception(message="Error during initialization of Database", config=None)
            raise e

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
        # get response
        try: 
            response = self.client.responses.create(
                model=AppConfig.MODEL, 
                input=input_list, 
                user=config["metadata"]["user"],
                previous_response_id=s["previous_conversation_id"],
                tools=[_01_t_orcgraph_identify_create_usecase, _01_t_orcgraph_identify_otherscenarios_usecase ]
            )
        except KeyError as ke: 
            pass
        return {"current_conversation_id":response.id,
                "response": response
                }
    def _02_branch_for_usecase(self, state: StateSchema ) -> str: 
        """
        Conditional edge that routes graph flow to appropriate use case, or to failure scenario
        """
        # for output in  state.response["output"]: 
        #     if 


    
    def compile(self) -> bool:
        """
        Method to initialize, compile and assign compiled state graph as attribute in graph wrapper object
        """
        try: 
            
            checkpointer = InMemorySaver()
            graph_builder = StateGraph(StateSchema)
            graph_builder.add_node("_get_short_term_memory", self._preprocess_get_short_term_memory_for_conversationid)
            graph_builder.add_node("01a_add_usecase_context",self._01a_node_add_identfyusecase_sysprompt )
            graph_builder.add_node("_01_process_usecase_identification", self._01_node_identify_usecase)
            graph_builder.add_node("_update_short_term_memory", self._postprocess_update_short_term_memory_for_conversation)
            graph_builder.add_edge(START, "_get_short_term_memory")
            graph_builder.add_edge("_get_short_term_memory", "01a_add_usecase_context")
            graph_builder.add_edge("01a_add_usecase_context","_01_process_usecase_identification" )
            graph_builder.add_edge("_01_process_usecase_identification" ,"_update_short_term_memory" )
            graph_builder.add_edge("_update_short_term_memory", END)

            self.compiledgraph= graph_builder.compile(checkpointer=checkpointer)
        except Exception as e: 
            self.log.log_exception(message="Exception occured during creation of graph" + str(e), config=None)
            raise e

    async def _preprocess_get_short_term_memory_for_conversationid(self,state: StateSchema,  config: RunnableConfig) -> StateSchema: 
            """
            Utility method to get state for a particular session
            """
            try:
                self.log.log_info("Retrieving short term meomry for session id", config )
                
                async with self.mongo_async_client.start_session(causal_consistency=True) as session:
                    response = await  self.db_collection.find_one(dict(conversation_id=config["configurable"]["thread_id"]), session=session)
                    
                    return {"attribute_state": response}
            except Exception as e: 
                self.log.log_exception(message="Error during retrieval of short term memory for session id", config=config)
                                  
                return state        
    
    async def _postprocess_update_short_term_memory_for_conversation(self,state:StateSchema,  config:RunnableConfig) -> StateSchema:
        """
        Utility function to store session data into short term memory
        """
        try:                 
            self.log.log_info("Update/Upsert State information to short-term memory", config )
            
            async  with self.mongo_async_client.start_session( causal_consistency=True) as session: 
                if state["attribute_state"] is not None: 
                    update_record = self.db_collection.update_one(dict(conversation_id=config["configurable"]["thread_id"], object=None),
                        {"$set": {key:input[key] for key in state["attribute_state"].keys()}},
                        upsert=True, 
                        session=session) 
                    update_message = f"Update Record: No of documents matched: {update_record.matched_count}  Did Upsert Happen:{update_record.did_upsert} \
                        No of documents modified:{update_record.modified_count}"
                    self.log.log_info( update_message, config)
                return state
                
        except Exception as e: 
            self.log.log_exception(message="Error during updating short term memory ", config=config)
            return state

    def _get_runnable_config(self,config: GraphRunMetaSchema) -> RunnableConfig: 
        """
        return runnable config from graph metadata schema
        """
        return RunnableConfig(configurable=dict(thread_id=config.conversation_id), 
                                        metadata=dict(app_correlation_id=config.app_correlation_id, user=config.user),
                                        recursion_limit=100)

    async def invoke(self , input: StateSchema, graph_config: RunnableConfig | GraphRunMetaSchemaT )->StateSchema:
        """
            Invoke graph to get final response
        """ 
       
        response = await self.compiledgraph.ainvoke(input=input, config=self._get_runnable_config(graph_config))
        return response



    


