"""
Storage Service - In-Memory Document Storage

This service handles storing and retrieving document data.
We use in-memory storage (Python dictionary) for simplicity.

IMPORTANT: In-memory storage means data is lost when server restarts!
This is acceptable for this assignment but in production you'd use:
- SQLite for simple persistence
- PostgreSQL/MongoDB for production apps
- Redis for caching with TTL

Why in-memory for this assignment?
1. Simple to implement
2. Fast
3. No external dependencies
4. Meets assignment requirements
"""

import uuid
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class Document:
    """
    Data class representing a stored document.

    @dataclass automatically generates:
    - __init__ method
    - __repr__ method
    - Comparison methods

    This is cleaner than using a regular dictionary.
    """
    id: str
    filename: str
    content: str  # Extracted text content
    page_count: int
    character_count: int
    uploaded_at: datetime


class StorageService:
    """
    In-memory storage for documents.

    Uses a dictionary with document ID as key.
    Thread-safe for basic operations (Python GIL).
    """

    def __init__(self):
        """Initialize empty storage."""
        # Dictionary to store documents: {document_id: Document}
        self._documents: Dict[str, Document] = {}

        # Track the "current" document (most recently uploaded)
        # This simplifies the API - /ask doesn't need document_id
        self._current_document_id: Optional[str] = None

    def store_document(
        self,
        filename: str,
        content: str,
        page_count: int
    ) -> Document:
        """
        Store a new document and set it as current.

        Args:
            filename: Original filename
            content: Extracted text content
            page_count: Number of pages

        Returns:
            Document object with generated ID
        """
        # Generate unique ID using UUID4
        # UUID4 = random UUID, virtually no chance of collision
        document_id = str(uuid.uuid4())

        # Create document object
        document = Document(
            id=document_id,
            filename=filename,
            content=content,
            page_count=page_count,
            character_count=len(content),
            uploaded_at=datetime.utcnow()
        )

        # Store in dictionary
        self._documents[document_id] = document

        # Set as current document
        self._current_document_id = document_id

        return document

    def get_document(self, document_id: str) -> Optional[Document]:
        """
        Retrieve a document by ID.

        Args:
            document_id: The document's unique identifier

        Returns:
            Document if found, None otherwise
        """
        return self._documents.get(document_id)

    def get_current_document(self) -> Optional[Document]:
        """
        Get the most recently uploaded document.

        This is a convenience method so users don't need to
        track document IDs for simple single-document usage.

        Returns:
            Current document or None if no documents uploaded
        """
        if self._current_document_id:
            return self._documents.get(self._current_document_id)
        return None

    def has_documents(self) -> bool:
        """Check if any documents have been uploaded."""
        return len(self._documents) > 0

    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document by ID.

        Args:
            document_id: The document's unique identifier

        Returns:
            True if deleted, False if not found
        """
        if document_id in self._documents:
            del self._documents[document_id]
            # Update current document if we deleted it
            if self._current_document_id == document_id:
                # Set to most recent remaining document or None
                if self._documents:
                    self._current_document_id = list(self._documents.keys())[-1]
                else:
                    self._current_document_id = None
            return True
        return False

    def clear_all(self) -> None:
        """Clear all stored documents."""
        self._documents.clear()
        self._current_document_id = None


# Create singleton instance
# This ensures all parts of the app share the same storage
storage_service = StorageService()
