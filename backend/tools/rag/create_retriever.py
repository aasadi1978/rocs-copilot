import logging
from typing import List, Optional, Annotated

from langchain_core.documents import Document
from langchain_core.tools import tool, Tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings


"""
Summary

✅ No OpenAI API key needed - The system uses HuggingFace embeddings which run locally on your CPU, completely free with no API keys required.
✅ YouTube loading fixed - Videos load successfully by avoiding the add_video_info=True parameter that was causing HTTP 400 errors.
✅ Workflow is functional - The RAG workflow initialized successfully and responded to the query (though it didn't use the retriever in this case because the question was vague).

What Changed:
Switched from OpenAI embeddings to HuggingFace - Uses sentence-transformers/all-MiniLM-L6-v2 model that downloads once and runs locally
Fixed YouTube loader - Removed problematic add_video_info=True parameter
Improved error handling - Better messages throughout the workflow
The workflow is now fully compatible with your Anthropic-based setup and requires no OpenAI API key.
"""


class Retriever:
    """
    Retriever class to create a retriever based on the provided documents.
    The best practice would be to use doc_loader to load documents from various sources. Then
    pass the loaded documents to this class to create a retriever tool. The method get_retriever_tool
    can be used to get the retriever tool for use in a RAG workflow. Note that this class uses an in-memory vector store.
    """
    def __init__(
        self,
        documents: Optional[List[Document]] = [],
        name: str = "retriever",
        description: str = "Retrieves relevant documents from a knowledge base.",
        embedding: Optional[HuggingFaceEmbeddings] = None
    ):
        self.name = name
        self.description = description
        
        try:
            # Initialize embeddings using HuggingFace (free, no API key required)
            # Using a lightweight model that runs locally
            embedding = embedding or HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            # Create vector store
            self._vectorstore = InMemoryVectorStore(embedding=embedding)
            
            # Add documents
            if documents:
                self._vectorstore.add_documents(documents)
                logging.info(f"Added {len(documents)} documents to vector store")
            else:
                logging.warning("No documents provided to retriever")
            
            self._retriever = self._vectorstore.as_retriever()
            
        except Exception as e:
            logging.error(f"Error initializing retriever: {e}")
            if "sentence-transformers" in str(e).lower() or "huggingface" in str(e).lower():
                logging.error("HuggingFace embeddings issue detected. Please ensure:")
                logging.error("  1. Install required packages: pip install sentence-transformers")
                logging.error("  2. Ensure you have internet connection for first-time model download")
            raise
    
    def retrieve_context(self, query: str, k: int = 5) -> List[Document]:
        """Retrieve information to help answer a query."""

        try:
            retrieved_docs = self._vectorstore.similarity_search(query, k=k)

            serialized = "\n\n".join(
                (f"Source: {doc.metadata}\nContent: {doc.page_content}")
                for doc in retrieved_docs
            )

            return serialized, retrieved_docs
        
        except Exception as e:
            logging.error(f"Error during retrieval: {e}")
            return "", []
        
    def get_retriever_tool(self) -> Tool | None:
        """Create and return a retriever tool for the knowledge base."""
        try:
            # Create a proper tool function that works with LangGraph
            retriever = self._retriever
            tool_name = self.name
            tool_description = self.description
            
            @tool
            def retrieve_documents(query: Annotated[str, "The search query to find relevant documents"]) -> str:
                """Retrieve relevant documents from the knowledge base."""
                try:
                    docs = retriever.invoke(query)
                    if not docs:
                        return "No relevant documents found."
                    
                    # Format the documents into a readable string
                    formatted_docs = "\n\n".join(
                        f"Document {i+1}:\n{doc.page_content}\nMetadata: {doc.metadata}"
                        for i, doc in enumerate(docs)
                    )
                    return formatted_docs
                except Exception as e:
                    logging.error(f"Error retrieving documents: {e}")
                    return f"Error retrieving documents: {str(e)}"
            
            # Update the tool's name and description after creation
            retrieve_documents.name = tool_name
            retrieve_documents.description = tool_description
            
            logging.info(f"Retriever tool '{tool_name}' created successfully.")
            return retrieve_documents
        
        except Exception as e:
            logging.error(f"Error creating retriever tool: {e}")
            return None
    