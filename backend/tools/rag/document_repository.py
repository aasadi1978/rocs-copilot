import logging
import hashlib
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy import JSON, Column, DateTime, Integer, String
from initialize_app.create_app import SQLALCHEMY_DB
from langchain_core.documents import Document


class DocumentRepository(SQLALCHEMY_DB.Model):
    """
    SQLAlchemy ORM for managing split document persistence.
    Stores processed and split documents to avoid reprocessing.
    """

    __tablename__ = "document_cache"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_hash = Column(String(64), index=True, nullable=False, unique=True)  # Hash of source path
    source_path = Column(String(2000), nullable=False)  # Original file path or URL
    split_documents = Column(JSON, nullable=False)  # List of serialized Document objects
    document_count = Column(Integer, nullable=False)  # Number of split documents
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    chunk_size = Column(Integer, default=1000)  # Store chunking parameters
    chunk_overlap = Column(Integer, default=200)

    def __init__(self, **kwargs):
        self.source_hash = kwargs.get("source_hash")
        self.source_path = kwargs.get("source_path")
        self.split_documents = kwargs.get("split_documents", [])
        self.document_count = kwargs.get("document_count", 0)
        self.timestamp = kwargs.get("timestamp", datetime.now())
        self.chunk_size = kwargs.get("chunk_size", 1000)
        self.chunk_overlap = kwargs.get("chunk_overlap", 200)

    @staticmethod
    def _generate_source_hash(source_path: str, chunk_size: int, chunk_overlap: int) -> str:
        """Generate a unique hash for the source path and chunking parameters."""
        hash_input = f"{source_path}:{chunk_size}:{chunk_overlap}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    @staticmethod
    def _serialize_documents(documents: List[Document]) -> List[Dict[str, Any]]:
        """Convert LangChain Document objects to JSON-serializable dicts."""
        serialized = []
        for doc in documents:
            doc_dict = {
                "page_content": doc.page_content,
                "metadata": doc.metadata
            }
            serialized.append(doc_dict)
        return serialized

    @staticmethod
    def _deserialize_documents(serialized: List[Dict[str, Any]]) -> List[Document]:
        """Convert serialized dicts back to LangChain Document objects."""
        documents = []
        for doc_dict in serialized:
            doc = Document(
                page_content=doc_dict.get("page_content", ""),
                metadata=doc_dict.get("metadata", {})
            )
            documents.append(doc)
        return documents

    @classmethod
    def get_cached_documents(cls, source_path: str, chunk_size: int = 1000, 
                           chunk_overlap: int = 200) -> List[Document] | None:
        """
        Retrieve cached split documents for a given source.
        Returns List[Document] if found, None otherwise.
        """
        try:
            source_hash = cls._generate_source_hash(source_path, chunk_size, chunk_overlap)
            record = cls.query.filter(cls.source_hash == source_hash).first()
            
            if record:
                logging.info(f"Cache hit: Found {record.document_count} cached documents for {source_path}")
                return cls._deserialize_documents(record.split_documents)
            else:
                logging.info(f"Cache miss: No cached documents found for {source_path}")
                return None
                
        except Exception as e:
            logging.error(f"Error retrieving cached documents for {source_path}: {e}")
            return None

    @classmethod
    def save_documents(cls, source_path: str, documents: List[Document], 
                      chunk_size: int = 1000, chunk_overlap: int = 200) -> 'DocumentRepository':
        """
        Save split documents to the cache.
        If a record already exists for this source, it will be updated.
        """
        try:
            source_hash = cls._generate_source_hash(source_path, chunk_size, chunk_overlap)
            
            # Check if record exists
            existing_record: DocumentRepository = cls.query.filter(cls.source_hash == source_hash).first()
            
            if existing_record:
                # Update existing record
                existing_record.split_documents = cls._serialize_documents(documents)
                existing_record.document_count = len(documents)
                existing_record.timestamp = datetime.now()
                existing_record.chunk_size = chunk_size
                existing_record.chunk_overlap = chunk_overlap
                SQLALCHEMY_DB.session.commit()
                logging.info(f"Updated cache: {len(documents)} documents for {source_path}")
                return existing_record
            else:
                # Create new record
                record = cls(
                    source_hash=source_hash,
                    source_path=str(source_path),
                    split_documents=cls._serialize_documents(documents),
                    document_count=len(documents),
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
                SQLALCHEMY_DB.session.add(record)
                SQLALCHEMY_DB.session.commit()
                SQLALCHEMY_DB.session.refresh(record)
                logging.info(f"Cached {len(documents)} split documents for {source_path}")
                return record
                
        except Exception as e:
            logging.error(f"Error saving documents to cache for {source_path}: {e}")
            SQLALCHEMY_DB.session.rollback()
            raise

    @classmethod
    def clear_cache(cls, source_path: str | None = None):
        """
        Clear cached documents. If source_path is provided, clear only that source.
        Otherwise, clear all cached documents.
        """
        try:
            if source_path:
                # Delete all records for this source (any chunk configuration)
                deleted = cls.query.filter(cls.source_path == source_path).delete()
                SQLALCHEMY_DB.session.commit()
                logging.info(f"Cleared {deleted} cached document(s) for {source_path}")
            else:
                # Clear all
                deleted = cls.query.delete()
                SQLALCHEMY_DB.session.commit()
                logging.info(f"Cleared all {deleted} cached documents")
                
        except Exception as e:
            logging.error(f"Error clearing document cache: {e}")
            SQLALCHEMY_DB.session.rollback()
            raise

    @classmethod
    def list_cached_sources(cls) -> List[Dict[str, Any]]:
        """List all cached document sources with metadata."""
        try:
            records = cls.query.all()
            return [{
                "source_path": r.source_path,
                "document_count": r.document_count,
                "timestamp": r.timestamp.isoformat(),
                "chunk_size": r.chunk_size,
                "chunk_overlap": r.chunk_overlap
            } for r in records]
        except Exception as e:
            logging.error(f"Error listing cached sources: {e}")
            return []
