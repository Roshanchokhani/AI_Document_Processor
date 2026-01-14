"""
Document Routes - API Endpoints

This module defines the HTTP endpoints:
- POST /documents - Upload a PDF document
- POST /ask - Ask a question about the document

FastAPI uses Python type hints and Pydantic models to:
1. Validate request data automatically
2. Generate OpenAPI documentation
3. Provide editor autocomplete
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from app.models.schemas import (
    AskQuestionRequest,
    AskQuestionResponse,
    DocumentUploadResponse,
    ErrorResponse
)
from app.services.pdf_service import pdf_service
from app.services.storage_service import storage_service
from app.services.ai_service import ai_service
from app.config import settings

# Create router instance
# APIRouter is like a "mini FastAPI app" that groups related endpoints
router = APIRouter()


@router.post(
    "/documents",
    response_model=DocumentUploadResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file"},
        500: {"model": ErrorResponse, "description": "Server error"}
    },
    summary="Upload a PDF document",
    description="Upload a PDF document for question answering. The document text will be extracted and stored for later queries."
)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF document for Q&A.

    This endpoint:
    1. Validates the uploaded file (type, size)
    2. Extracts text from the PDF
    3. Stores the text for later Q&A

    Args:
        file: The uploaded PDF file (multipart form data)

    Returns:
        DocumentUploadResponse with document ID and stats

    Raises:
        HTTPException 400: Invalid file type, empty file, or extraction failed
        HTTPException 500: Server error during processing
    """
    try:
        # Step 1: Read file content
        content = await file.read()

        # Step 2: Validate file (type and size)
        pdf_service.validate_file(
            filename=file.filename or "unknown.pdf",
            file_size=len(content),
            max_size_mb=settings.MAX_FILE_SIZE_MB
        )

        # Step 3: Extract text from PDF
        extracted_text, page_count = pdf_service.extract_text(content)

        # Step 4: Store document
        document = storage_service.store_document(
            filename=file.filename or "unknown.pdf",
            content=extracted_text,
            page_count=page_count
        )

        # Step 5: Return success response
        return DocumentUploadResponse(
            success=True,
            message="Document uploaded and processed successfully",
            document_id=document.id,
            filename=document.filename,
            page_count=document.page_count,
            character_count=document.character_count
        )

    except ValueError as e:
        # Validation errors (bad file type, empty file, etc.)
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "PROCESSING_ERROR",
                "message": f"Failed to process document: {str(e)}"
            }
        )


@router.post(
    "/ask",
    response_model=AskQuestionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "No document or invalid question"},
        500: {"model": ErrorResponse, "description": "AI service error"}
    },
    summary="Ask a question about the document",
    description="Ask a question about the uploaded document. The AI will answer based ONLY on the document content."
)
async def ask_question(request: AskQuestionRequest):
    """
    Ask a question about the uploaded document.

    This endpoint:
    1. Retrieves the current document
    2. Sends document + question to OpenAI
    3. Returns grounded answer

    Args:
        request: AskQuestionRequest containing the question

    Returns:
        AskQuestionResponse with the AI-generated answer

    Raises:
        HTTPException 400: No document uploaded or invalid question
        HTTPException 500: AI service error
    """
    try:
        # Step 1: Check if API key is configured
        if not ai_service.validate_api_key():
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error": "CONFIGURATION_ERROR",
                    "message": "OpenAI API key is not configured. Please set OPENAI_API_KEY environment variable."
                }
            )

        # Step 2: Get current document
        document = storage_service.get_current_document()

        if not document:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "NO_DOCUMENT",
                    "message": "No document has been uploaded. Please upload a PDF document first using POST /documents"
                }
            )

        # Step 3: Get AI answer
        answer = ai_service.answer_question(
            document_content=document.content,
            question=request.question
        )

        # Step 4: Return response
        return AskQuestionResponse(
            success=True,
            question=request.question,
            answer=answer,
            document_id=document.id
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        # Validation errors from AI service
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        # AI service errors
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "AI_SERVICE_ERROR",
                "message": str(e)
            }
        )
