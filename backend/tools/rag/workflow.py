import logging
from pathlib import Path
from typing import List, Union
# from langchain_openai import ChatOpenAI as AIChatClass
from langchain_anthropic import ChatAnthropic as AIChatClass
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv

from utils.draw_graph import disp_state_graph
load_dotenv()

from models import llm_basic
from tools.rag.doc_loader import DocLoader
from tools.rag.grade_docs import grade_documents
from tools.rag.create_retriever import Retriever
from tools import TOOLS


class Workflow:
    """Singleton Workflow class for RAG operations including document retrieval and question answering.
    
    - Fetch and preprocess documents that will be used for retrieval.
    - Index those documents for semantic search and create a retriever tool for the agent.
    - Build an agentic RAG system that can decide when to use the retriever tool.
    """

    _instance = None
    _llm_model: AIChatClass = None
    _workflow_graph: StateGraph = None
    _retriever: Retriever = None
    _doc_loader: DocLoader = None
    _tools: dict[str, List[ToolNode]] = TOOLS.tools
    _llm_with_tools: AIChatClass = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Workflow, cls).__new__(cls)
            cls._instance._llm_model = llm_basic
            cls._instance._workflow_graph = None
            cls._instance._retriever = None
            cls._instance._doc_loader = None
            cls._instance._tools = TOOLS.tools
            cls._instance._llm_with_tools = None
        return cls._instance

    def __init__(self):
        pass

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the Workflow."""
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def initialize(self,
                   data_sources: Union[List[Union[str, Path]], None] = None,
                   name: str = "Workflow",
                   description: str = "Workflow for FenixBot question answering with document retrieval and grading."):

        """ Initialize the RAG workflow with data sources, retriever, and LLM model."""

        try:
            if not data_sources:
                raise ValueError("data_sources cannot be None or empty.")
            
            self._doc_loader: DocLoader = DocLoader(data_sources=data_sources)
            self._doc_loader.load_docs()

            if not self._doc_loader.documents:
                raise ValueError("No documents were loaded. Please check your data sources and ensure they are accessible.")

            self._retriever = Retriever(documents=self._doc_loader.documents, 
                                        name=name, 
                                        description=description)
            
            retriever_tool = self._retriever.get_retriever_tool()
            if not retriever_tool:
                raise ValueError("Failed to create retriever tool. Check the logs for details.")
            
            self._tools.setdefault("retriever_tool", []).append(retriever_tool)
            self._llm_with_tools = self._llm_model.bind_tools(self._tools)
            
            logging.info(f"Workflow initialized successfully with {len(self._doc_loader.documents)} documents.")

        except Exception as e:
            logging.error(f"Error initializing workflow: {e}")
            raise  # Re-raise the exception so the caller knows initialization failed

    def generate_query_or_respond(self, state: MessagesState):
        """Call the model to generate a response based on the current state. Given
        the question, it will decide to retrieve using the retriever tool, or simply respond to the user.
        """
        response = self._llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def rewrite_question(self, state: MessagesState):
        """Rewrite the original user question.
            Build the rewrite_question node. The retriever tool can return potentially irrelevant documents, which indicates a need to 
            improve the original user question. To do so, we will call the rewrite_question node:
        """

        REWRITE_PROMPT = (
            "Look at the input and try to reason about the underlying semantic intent / meaning.\n"
            "Here is the initial question:"
            "\n ------- \n"
            "{question}"
            "\n ------- \n"
            "Formulate an improved question:"
        )

        messages = state["messages"]
        question = messages[0].content
        prompt = REWRITE_PROMPT.format(question=question)
        response = self._llm_model.invoke([{"role": "user", "content": prompt}])
        return {"messages": [HumanMessage(content=response.content)]}


    def generate_answer(self, state: MessagesState):
        """Generate an answer."""

        GENERATE_PROMPT = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer the question. "
            "If you don't know the answer, just say that you don't know. "
            "Use three sentences maximum and keep the answer concise.\n"
            "Question: {question} \n"
            "Context: {context}"
        )

        question = state["messages"][0].content
        context = state["messages"][-1].content
        prompt = GENERATE_PROMPT.format(question=question, context=context)
        response = self._llm_model.invoke([{"role": "user", "content": prompt}])
        return {"messages": [response]}

    def build_graph(self):

        """Build the RAG workflow graph with decision nodes and edges.
        
        Now we'll assemble all the nodes and edges into a complete graph:
        Start with a generate_query_or_respond and determine if we need to call retriever_tool
        Route to next step using tools_condition:
        If generate_query_or_respond returned tool_calls, call retriever_tool to retrieve context
        Otherwise, respond directly to the user
        Grade retrieved document content for relevance to the question (grade_documents) and route to next step:
        If not relevant, rewrite the question using rewrite_question and then call generate_query_or_respond again
        If relevant, proceed to generate_answer and generate final response using the ToolMessage with the retrieved document context
        
        """

        if not self._retriever:
            raise ValueError("Retriever is not initialized. Please call initialize() first with valid data sources.")
        
        retriever_tool = self._retriever.get_retriever_tool()
        if not retriever_tool:
            raise ValueError("Failed to get retriever tool. Check initialization logs for details.")

        decision_flow = StateGraph(MessagesState)

        # Define the nodes we will cycle between
        decision_flow.add_node(self.generate_query_or_respond)
        decision_flow.add_node("retrieve", ToolNode([retriever_tool]))
        decision_flow.add_node(self.rewrite_question)
        decision_flow.add_node(self.generate_answer)

        decision_flow.add_edge(START, "generate_query_or_respond")

        # Decide whether to retrieve
        decision_flow.add_conditional_edges(
            "generate_query_or_respond",
            # Assess LLM decision (call `retriever_tool` tool or respond to the user)
            tools_condition,
            {
                # Translate the condition outputs to nodes in our graph
                "tools": "retrieve",
                END: END,
            },
        )

        # Edges taken after the `action` node is called.
        decision_flow.add_conditional_edges(
            "retrieve",
            # Assess agent decision
            grade_documents,
        )
        decision_flow.add_edge("generate_answer", END)
        decision_flow.add_edge("rewrite_question", "generate_query_or_respond")

        # Compile
        self._workflow_graph = decision_flow.compile()

        disp_state_graph(self._workflow_graph, mmd_file_name="rag_workflow_graph.mmd")
        
    def run_example(self):
        """Example method showing how to run a single query through the workflow."""
        for chunk in self._workflow_graph.stream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "What is ROCS and what does it stand for?",
                    }
                ]
            }
        ):
            for node, update in chunk.items():
                print("Update from node", node)
                update["messages"][-1].pretty_print()
                print("\n\n")

    def stream_chat(self, messages: list):
        """Stream chat responses with conversation history.
        
        Args:
            messages: List of message dictionaries or BaseMessage objects representing the conversation history
            
        Yields:
            Tuples of (node_name, message_content) for each step in the workflow
        """
        if not self._workflow_graph:
            raise ValueError("Graph not built. Call build_graph() first.")
        
        for chunk in self._workflow_graph.stream({"messages": messages}):
            for node, update in chunk.items():
                # Yield the node name and the latest message
                if "messages" in update and update["messages"]:
                    latest_message = update["messages"][-1]
                    yield (node, latest_message)

    def invoke_chat(self, messages: list):
        """Invoke the workflow and return the final response.
        
        Args:
            messages: List of message dictionaries or BaseMessage objects representing the conversation history
            
        Returns:
            The final state after processing all nodes
        """
        if not self._workflow_graph:
            raise ValueError("Graph not built. Call build_graph() first.")
        
        return self._workflow_graph.invoke({"messages": messages})

RAG_WORKFLOW_INSTANCE = Workflow.get_instance()