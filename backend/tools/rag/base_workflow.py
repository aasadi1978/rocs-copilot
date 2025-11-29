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
from typing import List, Union, Optional
from langchain_anthropic import ChatAnthropic as AIChatClass
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv

from models import llm_basic
from doc_loader.doc_importer import DocumentImporter
from doc_loader.grade_docs import grade_documents
from utils.draw_graph import disp_state_graph
from tools.rag.create_retriever import Retriever

load_dotenv(override=True)


class BaseWorkflow(ABC):
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
        self._decision_flow: Optional[StateGraph] = None

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
        """
        pass

    @abstractmethod
    def run_example(self) -> None:
        """Run an example demonstrating the workflow's capabilities.
        
        This method should provide a simple demonstration of how to use
        the workflow, useful for testing and documentation.
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

    def generate_query_or_respond(self, state: MessagesState):
        """Call the model to generate a response based on the current state.
        
        Given the question, it will decide to retrieve using the retriever tool,
        or simply respond to the user.
        
        Args:
            state: Current message state
            
        Returns:
            Updated state with model response
        """
        response = self._llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def rewrite_question(self, state: MessagesState):
        """Rewrite the original user question for better retrieval.
        
        The retriever tool can return potentially irrelevant documents, which indicates
        a need to improve the original user question. This node rewrites the question
        to improve semantic matching.
        
        Args:
            state: Current message state
            
        Returns:
            Updated state with rewritten question
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
        """Generate an answer using retrieved context.
        
        Args:
            state: Current message state including question and retrieved context
            
        Returns:
            Updated state with generated answer
        """
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

    def _assemble_decision_flow(self) -> StateGraph:
        """Assemble the decision flow graph with nodes and edges.
        
        This method creates the base RAG decision flow. Subclasses can override this
        to add additional nodes or modify the flow before compilation.
        
        Returns:
            Assembled StateGraph ready for compilation
            
        Raises:
            ValueError: If retriever tool not available
        """
        retriever_tool = self._get_retriever_tool()
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
            # Assess LLM decision (call retriever_tool or respond to the user)
            tools_condition,
            {
                # Translate the condition outputs to nodes in our graph
                "tools": "retrieve",
                END: END,
            },
        )

        # Edges taken after the retrieve node is called
        decision_flow.add_conditional_edges(
            "retrieve",
            # Assess agent decision
            grade_documents,
        )
        decision_flow.add_edge("generate_answer", END)
        decision_flow.add_edge("rewrite_question", "generate_query_or_respond")

        # Usage Examples: Advanced: Custom Workflow by subclassing BaseWorkflow
        # Basic: Standard Workflow
        # workflow = Workflow()
        # workflow.initialize(data_sources=[...])
        # workflow.build_graph()  # Uses default flow
        # 
        # class CustomWorkflow(BaseWorkflow):
        #     def _assemble_decision_flow(self):
        #         # Get the base decision flow
        #         decision_flow = super()._assemble_decision_flow()
                
        #         # Add custom nodes
        #         decision_flow.add_node("summarize", self.summarize_results)
        #         decision_flow.add_node("translate", self.translate_answer)
                
        #         # Add custom edges
        #         decision_flow.add_edge("generate_answer", "summarize")
        #         decision_flow.add_edge("summarize", "translate")
        #         decision_flow.add_edge("translate", END)
        # 
        #         return decision_flow
        # 
        # Advanced: Modify flow before compilation:
        # workflow.initialize(data_sources=[...])
        # # Manually assemble if needed
        # workflow._decision_flow = workflow._assemble_decision_flow()
        # # Add custom modifications
        # workflow._decision_flow.add_node("custom_step", custom_function)
        # # Then compile
        # workflow._workflow_graph = workflow._decision_flow.compile()

        return decision_flow

    def build_graph(self, graph_name: str = "workflow_graph"):
        """Build the RAG workflow graph by assembling and compiling the decision flow.
        
        This method:
        1. Calls _assemble_decision_flow() to create the graph structure
        2. Stores it in self._decision_flow for potential modifications
        3. Compiles it into the executable workflow graph
        
        Subclasses can override _assemble_decision_flow() to customize the graph structure
        before compilation.
        
        Args:
            graph_name: Name for the generated graph diagram file
        """
        # Assemble the decision flow (can be overridden by subclasses)
        self._decision_flow = self._assemble_decision_flow()
        
        # Compile the decision flow into executable graph
        self._workflow_graph = self._decision_flow.compile()

        disp_state_graph(self._workflow_graph, mmd_file_name=f"{graph_name}.mmd")

    def stream_chat(self, messages: list):
        """Stream chat responses with conversation history.
        
        Args:
            messages: List of message dictionaries or BaseMessage objects representing the conversation history
            
        Yields:
            Tuples of (node_name, message_content) for each step in the workflow
            
        Raises:
            ValueError: If graph not built
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
            
        Raises:
            ValueError: If graph not built
        """
        if not self._workflow_graph:
            raise ValueError("Graph not built. Call build_graph() first.")
        
        return self._workflow_graph.invoke({"messages": messages})

