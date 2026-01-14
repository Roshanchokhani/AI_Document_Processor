"""
PDF Service - Handles PDF text extraction

This service is responsible for:
1. Validating PDF files
2. Extracting text content from PDFs
3. Handling PDF-related errors

Why separate this into its own service?
- Single Responsibility: This service only handles PDF operations
- Testability: Can test PDF extraction independently
- Reusability: Can use this service elsewhere if needed
"""

import io
from PyPDF2 import PdfReader
from typing import Tuple


class PDFService:
    """
    Service for handling PDF operations.
    """

    def extract_text(self, file_content: bytes) -> Tuple[str, int]:
        """
        Extract text content from a PDF file.

        Args:
            file_content: Raw bytes of the PDF file

        Returns:
            Tuple of (extracted_text, page_count)

        Raises:
            ValueError: If PDF is empty or cannot be read
            Exception: For other PDF processing errors

        How it works:
        1. Create a BytesIO object from the raw bytes (makes it file-like)
        2. Use PdfReader to parse the PDF structure
        3. Loop through each page and extract text
        4. Combine all text and return with page count
        """
        try:
            # BytesIO allows us to treat bytes as a file object
            # PdfReader expects a file-like object, not raw bytes
            pdf_file = io.BytesIO(file_content)

            # Create PDF reader object
            reader = PdfReader(pdf_file)

            # Get number of pages
            page_count = len(reader.pages)

            if page_count == 0:
                raise ValueError("PDF file contains no pages")

            # Extract text from each page
            extracted_text = ""
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    # Add page separator for clarity
                    extracted_text += f"\n--- Page {page_num + 1} ---\n"
                    extracted_text += page_text

            # Check if we got any text
            if not extracted_text.strip():
                raise ValueError(
                    "Could not extract text from PDF. "
                    "The PDF might be scanned/image-based or empty."
                )

            return extracted_text.strip(), page_count

        except ValueError:
            # Re-raise ValueError as-is (our custom errors)
            raise
        except Exception as e:
            # Wrap other errors with more context
            raise Exception(f"Failed to process PDF: {str(e)}")

    def validate_file(self, filename: str, file_size: int, max_size_mb: int = 10) -> None:
        """
        Validate that the uploaded file meets requirements.

        Args:
            filename: Original filename
            file_size: Size in bytes
            max_size_mb: Maximum allowed size in megabytes

        Raises:
            ValueError: If validation fails
        """
        # Check file extension
        if not filename.lower().endswith('.pdf'):
            raise ValueError(
                f"Invalid file type. Expected PDF, got: {filename.split('.')[-1] if '.' in filename else 'unknown'}"
            )

        # Check file size
        max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
        if file_size > max_size_bytes:
            raise ValueError(
                f"File too large. Maximum size is {max_size_mb}MB, "
                f"got {file_size / (1024 * 1024):.2f}MB"
            )

        if file_size == 0:
            raise ValueError("File is empty")


# Create singleton instance
# Singleton pattern: Only one instance exists throughout the app
pdf_service = PDFService()
