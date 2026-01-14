"""
Pydantic Schemas for Request/Response Validation

Pydantic is a data validation library that:
1. Validates incoming request data automatically
2. Converts data to correct types
3. Generates clear error messages
4. Creates automatic API documentation

These schemas define the SHAPE of data going in and out of your API.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ============ Request Schemas ============

class AskQuestionRequest(BaseModel):
    """
    Schema for the POST /ask endpoint request body.

    Example JSON:
    {
        "question": "What is the main topic of the document?"
    }
    """
    question: str = Field(
        ...,  # ... means this field is required
        min_length=1,
        max_length=1000,
        description="The question to ask about the uploaded document",
        examples=["What is the main topic of the document?"]
    )


# ============ Response Schemas ============

class DocumentUploadResponse(BaseModel):
    """
    Response returned after successful document upload.
    """
    success: bool = Field(description="Whether upload was successful")
    message: str = Field(description="Human-readable status message")
    document_id: str = Field(description="Unique identifier for the document")
    filename: str = Field(description="Original filename")
    page_count: int = Field(description="Number of pages extracted")
    character_count: int = Field(description="Total characters extracted")


class AskQuestionResponse(BaseModel):
    """
    Response returned after asking a question.
    """
    success: bool = Field(description="Whether the question was processed successfully")
    question: str = Field(description="The original question asked")
    answer: str = Field(description="AI-generated answer based on the document")
    document_id: str = Field(description="ID of the document used for answering")


class ErrorResponse(BaseModel):
    """
    Standard error response format.

    Having a consistent error format makes it easier for
    frontend developers to handle errors.
    """
    success: bool = Field(default=False)
    error: str = Field(description="Error type/code")
    message: str = Field(description="Human-readable error description")
    details: Optional[str] = Field(default=None, description="Additional error details")


class HealthCheckResponse(BaseModel):
    """
    Health check endpoint response.
    Useful for monitoring and deployment checks.
    """
    status: str = Field(description="Service status")
    version: str = Field(description="API version")
    timestamp: datetime = Field(description="Current server time")
