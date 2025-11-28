import logging
from pathlib import Path
from typing import List, Union

from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tools.rag.load_video_audio import transcribe_audio
from tools.rag.load_url import transcribe_url
from tools.rag.document_repository import DocumentRepository


class DocLoader:

    def __init__(
            self, 
            data_sources: Union[List[Union[str, Path]], None] = None,
            chunk_size: int = 1000,
            chunk_overlap: int = 200,
            use_cache: bool = True):
        
        self.__data_sources = data_sources or []
        self.__documents = []
        self.__chunk_size = chunk_size
        self.__chunk_overlap = chunk_overlap
        self.__use_cache = use_cache
    
    @property
    def documents(self) -> List[Document]:
        return self.__documents

    def load_doc(self, file_path: Union[str, Path]) -> List[Document]:
        """
        This function detects the file format and loads into langchain document using an appropriate langchain module.
        Uses caching to avoid reprocessing the same documents.
        """
        
        source_path = str(file_path)
        
        # Check cache first if enabled
        if self.__use_cache:
            cached_docs = DocumentRepository.get_cached_documents(
                source_path, 
                self.__chunk_size, 
                self.__chunk_overlap
            )
            if cached_docs:
                return cached_docs
        
        # Handle URLs separately
        if isinstance(file_path, str) and str(file_path).lower().startswith("http"):
            raw_documents = transcribe_url(file_path)
        else:
            # Handle file paths
            file_path = Path(file_path).resolve()
            raw_documents = []

            if file_path.suffix.lower() == ".pdf":
                try:
                    loader = PyPDFLoader(str(file_path))
                    raw_documents = loader.load()
                except Exception as e:
                    logging.info(f"Error loading {file_path}: {e}")

            elif file_path.suffix.lower() == ".pptx":
                try:
                    loader = UnstructuredPowerPointLoader(str(file_path))
                    raw_documents = loader.load()
                except Exception as e:
                    logging.info(f"Error loading {file_path}: {e}")

            elif file_path.suffix.lower() == ".docx":
                try:
                    loader = UnstructuredWordDocumentLoader(str(file_path))
                    raw_documents = loader.load()
                except Exception as e:
                    logging.info(f"Error loading {file_path}: {e}")

            elif file_path.suffix.lower() in [".mp4", ".mp3", ".wav", ".m4a", ".avi", ".mov"]:
                raw_documents = transcribe_audio(file_path)
        
        # Split the documents
        split_documents = self.split_docs(raw_documents)
        
        # Cache the split documents if caching is enabled
        if self.__use_cache and split_documents:
            try:
                DocumentRepository.save_documents(
                    source_path, 
                    split_documents, 
                    self.__chunk_size, 
                    self.__chunk_overlap
                )
            except Exception as e:
                logging.warning(f"Failed to cache documents for {source_path}: {e}")

        return split_documents

    def load_docs(self, 
                  data_sources: Union[List[Union[str, Path]], None] = None) -> List[Document]:
        """
        Input:
            data_sources: Optional list of file paths, directories or URLs to load documents from.

        This function detects the file format in a provided directory and/or file paths and loads into
        langchain Document using an appropriate langchain module. Supporting file types include 
        PDF, PPTX, DOCX, YouTube URLs, web pages, and audio/video files.
        """

        data_sources =  data_sources or []
        data_sources.extend(self.__data_sources)

        documents = []
        source_document_files = []

        for src_pth  in data_sources:

            src_path = Path(src_pth).resolve()
    
            if src_path.is_dir() and src_path.exists():
                source_document_files.extend([p for p in src_path.iterdir() if p.is_file()])

            elif src_path.is_file() and src_path.exists():
                source_document_files.append(src_path)
            else:
                # If the path does not exist, still append it to attempt loading later.
                # It is most likely a URL.
                source_document_files.append(src_pth)
        
        for file_path in set(source_document_files):

            logging.info(f"Loading document: {file_path}")
            # load_doc now handles caching and splitting internally
            self.__documents.extend(self.load_doc(file_path))

    def split_docs(self, documents: List[Document]) -> List[Document]:
        """
        This function splits the documents into smaller chunks using langchain text splitters.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.__chunk_size,
            chunk_overlap=self.__chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

        doc_splits = text_splitter.split_documents(documents)
        
        if doc_splits:
            some_characters = doc_splits[0].page_content.strip()[:1000]
            some_characters = some_characters.replace("\n", " ").replace("\r", " ")
            logging.info(f"Split into {len(doc_splits)} documents: {some_characters}")
        else:
            logging.warning("No documents were split.")
        
        return doc_splits
