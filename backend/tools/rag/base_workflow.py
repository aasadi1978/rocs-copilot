"""Base Workflow class providing common RAG workflow infrastructure.

This abstract base class encapsulates common patterns used across RAG-based workflows including:
- Document loading and preprocessing via DocumentImporter
- LLM model integration with tool binding
- State graph building for agentic RAG
- Query generation, document retrieval, and answer generation
- Conversation management (streaming and invocation)
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Union, Optional, Annotated, TypedDict
from langchain_anthropic import ChatAnthropic as AIChatClass
from langchain_core.documents import Document
from langchain_core.messages import AnyMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv

from models import llm_basic
from doc_loader.doc_importer import DocumentImporter
from utils.draw_graph import disp_state_graph
from tools.rag.create_retriever import Retriever

load_dotenv(override=True)


class RAGState(TypedDict):
    """Represents the state of a RAG conversation session.
    
    Attributes:
        messages: Conversation history with automatic message merging
        conversation_id: Unique identifier for the conversation session
        topic: Main topic or subject being discussed (e.g., 'news', 'research', 'qa')
        context: Additional context or metadata for the RAG workflow
        retrieved_docs: Count of documents retrieved in current session
    """
    messages: Annotated[List[AnyMessage], add_messages]
    conversation_id: str
    topic: str
    context: Optional[str]
    retrieved_docs: int


class BaseWorkFlow(ABC):
    """Abstract base class for RAG workflow types.
    
    Provides common RAG infrastructure:
    - Document loading via DocumentImporter
    - LLM model management with tool binding
    - State graph building and execution
    - Query/response generation
    - Document grading and question rewriting
    - Streaming and invocation interfaces
    """

    def __init__(self, llm_model: Optional[AIChatClass] = None):
        """Initialize the workflow.
        
        Args:
            llm_model: Optional LLM model to use. If not provided, uses default llm_basic
        """
        self._llm_model = llm_model if llm_model else llm_basic
        self._doc_loader: Optional[DocumentImporter] = None
        self._documents: Optional[List[Document]] = None
        self._initialized: bool = False
        self._workflow_graph: Optional[StateGraph] = None
        self._llm_with_tools: Optional[AIChatClass] = None
        self._retriever: Optional[Retriever] = None
        self._tools: dict = {}

    def _load_documents(self,
                       data_sources: Union[List[Union[str, Path]], None] = None,
                       chunk_size: int = 1000,
                       chunk_overlap: int = 200,
                       use_cache: bool = True) -> List[Document]:
        """Load and preprocess documents from data sources.
        
        Args:
            data_sources: List of file paths, URLs, or directories to load documents from
            chunk_size: Size of document chunks for processing
            chunk_overlap: Overlap between chunks
            use_cache: Whether to cache loaded documents
            
        Returns:
            List of loaded Document objects
            
        Raises:
            ValueError: If data_sources is None/empty or no documents could be loaded
        """
        if not data_sources:
            raise ValueError("data_sources cannot be None or empty.")
        
        logging.info(f"Loading documents from {len(data_sources)} sources...")
        
        self._doc_loader = DocumentImporter(
            data_sources=data_sources,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            use_cache=use_cache
        )
        
        self._doc_loader.load_docs()
        self._documents = self._doc_loader.documents
        
        if not self._documents:
            raise ValueError(
                "No documents were loaded. Please check your data sources "
                "and ensure they are accessible."
            )
        
        logging.info(f"Successfully loaded {len(self._documents)} document chunks.")
        return self._documents

    def _setup_retriever_and_tools(self,
                                   name: str = "Retriever",
                                   description: str = "Retrieves relevant documents based on the query",
                                   additional_tools: Optional[dict] = None) -> None:
        """Setup retriever tool and bind all tools to LLM.
        
        Args:
            name: Name for the retriever tool
            description: Description of what the retriever does
            additional_tools: Optional dict of additional tools to bind (e.g., {'tool_name': [tool_list]})
            
        Raises:
            ValueError: If documents not loaded or retriever creation fails
        """
        if not self._documents:
            raise ValueError("Documents must be loaded before setting up retriever. Call _load_documents() first.")
        
        # Create retriever from loaded documents
        self._retriever = Retriever(
            documents=self._documents,
            name=name,
            description=description
        )
        
        retriever_tool = self._retriever.get_retriever_tool()
        if not retriever_tool:
            raise ValueError("Failed to create retriever tool. Check the logs for details.")
        
        # Initialize tools dict with retriever
        self._tools = {"retriever_tool": [retriever_tool]}
        
        # Add any additional tools provided
        if additional_tools:
            self._tools.update(additional_tools)
        
        # Bind all tools to the LLM model
        self._llm_with_tools = self._llm_model.bind_tools(
            [tool for tool_list in self._tools.values() for tool in tool_list]
        )
        
        logging.info(f"Retriever and tools setup complete. Total tools: {len(self._tools)}")

    @abstractmethod
    def initialize(self, **kwargs) -> None:
        """Initialize the workflow with necessary components.
        
        Each workflow type must implement this method to set up its specific
        components (retriever, summarizer, graph, etc.).
        
        Args:
            **kwargs: Workflow-specific initialization parameters
            
        Raises:
            ValueError: If initialization fails
        
        NOTE: This method must be overridden by subclasses to provide
        workflow-specific initialization logic.
        """
        pass

    @abstractmethod
    def run_example(self) -> None:
        """Run an example demonstrating the workflow's capabilities.
        
        This method should provide a simple demonstration of how to use
        the workflow, useful for testing and documentation.
        
        NOTE: This method must be overridden by subclasses to provide
        workflow-specific example logic.
        """
        pass

    def get_documents(self) -> Optional[List[Document]]:
        """Get the loaded documents.
        
        Returns:
            List of loaded documents, or None if not yet loaded
        """
        return self._documents

    def get_llm_model(self) -> AIChatClass:
        """Get the LLM model instance.
        
        Returns:
            The LLM model used by this workflow
        """
        return self._llm_model

    def _get_retriever_tool(self):
        """Get the retriever tool for this workflow.
        
        Returns:
            The retriever tool to be used in the graph
            
        Raises:
            ValueError: If retriever not initialized
        """
        if not self._retriever:
            raise ValueError("Retriever is not initialized. Please call initialize() first with valid data sources.")
        return self._retriever.get_retriever_tool()


    def generate_query_or_respond(self, state: RAGState):
        """Call the model to generate a response based on the current state.
        
        Given the question, it will decide to retrieve using the retriever tool,
        or simply respond to the user.
        
        Args:
            state: Current RAG state with messages and metadata
            
        Returns:
            Updated state with model response
        """
        response = self._llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def generate_answer(self, state: RAGState):
        """Generate an answer based on retrieved documents and user question.
        
        Args:
            state: Current RAG state with messages and metadata
        Returns:
            Updated state with generated answer message
        
        
        NOTE: This method can be overridden by subclasses to customize answer generation.
        """

        try:
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
            response = self._llm_with_tools.invoke([{"role": "user", "content": prompt}])

            return {"messages": [response]}
        
        except Exception as e:
            logging.error(f"Error generating answer: {e}")
            return {"messages": []}

    def assemble_decision_flow(self) -> StateGraph:
        """Assemble the decision flow graph with nodes and edges.
        
        This method creates the base RAG decision flow. Subclasses can override this
        to add additional nodes or modify the flow before compilation.
        
        Returns:
            Assembled StateGraph ready for compilation
            
        Raises:
            ValueError: If retriever tool not available
        
        NOTE: This method can be overridden by subclasses to customize the decision flow.
        """

        try:
            retriever_tool = self._get_retriever_tool()
            if not retriever_tool:
                raise ValueError("Failed to get retriever tool. Check initialization logs for details.")

            _state_graph = StateGraph(RAGState)

            # Define the nodes we will cycle between
            _state_graph.add_node(self.generate_query_or_respond)
            _state_graph.add_node("retrieve", ToolNode([retriever_tool]))
            
            _state_graph.add_edge(START, "generate_query_or_respond")

            # Decide whether to retrieve
            _state_graph.add_conditional_edges(
                "generate_query_or_respond",
                # Assess LLM decision (call retriever_tool or respond to the user)
                tools_condition,
                {
                    # Translate the condition outputs to nodes in our graph
                    "tools": "retrieve",
                    END: END,
                },
            )

            _state_graph.add_edge("retrieve", "generate_answer")
            _state_graph.add_edge("generate_answer", END)

        except Exception as e:

            logging.error(f"Error assembling decision flow: {e}")
            _state_graph = StateGraph(RAGState)
        
        return _state_graph


    def display_state_graph(self, graph_name: str = "workflow_graph"):
        """Visualize the state graph.
        
        This method compiles the decision flow into an executable graph
        and saves a visualization using disp_state_graph.
        """

        # Compile the decision flow into executable graph
        disp_state_graph(self._get_compiled_graph(), mmd_file_name=f"{graph_name}.mmd")
    
    def _get_compiled_graph(self):
        """Compile the decision flow into an executable graph."""
        self._workflow_graph = self._workflow_graph or self.assemble_decision_flow().compile()
        return self._workflow_graph

    
    def stream_chat(self, messages: List[RAGState] = []):
        """Stream chat responses with conversation history.
        
        Args:
            messages: List of message dictionaries or BaseMessage objects representing the conversation history
            
        Yields:
            Tuples of (node_name, message_content) for each step in the workflow
            
        Raises:
            ValueError: If graph not built
        """

        graph: StateGraph =  self._get_compiled_graph()

        if not graph:
            raise ValueError("Graph not built. Call compile_and_save_graph() first.")
        
        for chunk in graph.stream({"messages": messages}):
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
            
        Raises:
            ValueError: If graph not built
        """
        if not self._workflow_graph:
            raise ValueError("Graph not built. Call build_graph() first.")
        
        return self._workflow_graph.invoke({"messages": messages})

