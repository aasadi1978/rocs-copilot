import logging
from pathlib import Path
from typing import List, Union, Optional
from langchain_anthropic import ChatAnthropic as AIChatClass
from dotenv import load_dotenv

load_dotenv()

from tools.rag.base_workflow import BaseWorkFlow


class Workflow(BaseWorkFlow):
    """A RAG Workflow class for document retrieval and question answering.
    
    Extends BaseWorkFlow to provide:
    - Document retrieval using semantic search
    - Agentic RAG system with tool binding
    - Document grading for relevance
    - Question rewriting for better results
    """

    def __init__(self, llm_model: AIChatClass = None):
        """Initialize the RAG workflow.
        
        Args:
            llm_model: Optional LLM model to use. If not provided, uses default llm_basic
        """
        super().__init__(llm_model)

    def initialize(self,
                   data_sources: Union[List[Union[str, Path]], None] = None,
                   name: str = "Workflow",
                   description: str = "Workflow for FenixBot question answering with document retrieval and grading.",
                   chunk_size: int = 1000,
                   chunk_overlap: int = 200,
                   additional_tools: Optional[dict] = None):

        """Initialize the RAG workflow with data sources, retriever, and LLM model.
        
        Loads documents, creates a retriever tool for semantic search, and binds all tools to the LLM.
            
        Args:
            data_sources: List of file paths, URLs, or directories to load documents from
            name: Name for the workflow/retriever
            description: Description of the workflow/retriever
            chunk_size: Size of document chunks
            chunk_overlap: Overlap between chunks
            additional_tools: Optional dict of additional tools to bind beyond the retriever
        """

        try:
            # Use base class method to load documents
            self._load_documents(
                data_sources=data_sources,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                use_cache=True
            )

            # Use base class method to setup retriever and tools
            self._setup_retriever_and_tools(
                name=name,
                description=description,
                additional_tools=additional_tools
            )
            
            logging.info(f"RAG Workflow initialized successfully with {len(self._documents)} documents.")

        except Exception as e:
            logging.error(f"Error initializing workflow: {e}")
            raise

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

# Example usage:
# workflow = Workflow()
# workflow.initialize(data_sources=[...])
# workflow.build_graph()
# workflow.run_example()