# Purpose:
# This file implements the PDF and OCR document connector adapter.
#
# Why this file exists:
# Clinical discharge summaries, lab reports, and referral letters often arrive as 
# digital PDFs or scanned images. This connector extracts readable text from those 
# documents so the AI can search and reason over them.
#
# In simple terms:
# This is our document reader. It opens PDF files, checks if it can read the text directly,
# and if the file is just a scanned photo, it uses image-recognition (OCR) to read the words.

import os
import asyncio
from typing import Any, Dict
import pdfplumber
import pytesseract
from PIL import Image
from app.connectors.base import Connector, ExecutionStep, NormalizedResult

class PdfOcrConnector(Connector):
    def __init__(self, source_name: str = "pdf_ocr"):
        self.source_name = source_name
        self.base_dir = os.getenv("PDF_DOCS_DIR", "./data/documents")

    def _extract_text_from_pdf(self, file_path: str) -> str:
        extracted_text = ""
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                
                # If digital text exists on the page, use it
                if page_text and len(page_text.strip()) > 20:
                    extracted_text += page_text + "\n"
                else:
                    # Fallback: Convert PDF page to image and run OCR
                    page_image = page.to_image(resolution=300).original
                    ocr_text = pytesseract.image_to_string(page_image)
                    extracted_text += ocr_text + "\n"

        return extracted_text.strip()

    def _execute_sync(self, plan: ExecutionStep) -> NormalizedResult:
        # Resolve document file path securely
        file_path = os.path.join(self.base_dir, f"{plan.dataset_id}")

        # Directory traversal prevention
        if not os.path.abspath(file_path).startswith(os.path.abspath(self.base_dir)):
            raise PermissionError("Access to this document path is forbidden.")

        if not os.path.exists(file_path):
            return NormalizedResult(source=self.source_name, rows=[], columns=[])

        full_text = self._extract_text_from_pdf(file_path)

        # Apply keyword/filter search if provided
        # e.g., filters: {"contains": "cardiology"}
        rows = []
        keyword = plan.filters.get("contains", "").lower() if plan.filters else ""

        if not keyword or keyword in full_text.lower():
            rows.append({
                "document_id": plan.dataset_id,
                "file_path": file_path,
                "content": full_text,
                "char_count": len(full_text)
            })

        return NormalizedResult(
            source=self.source_name,
            rows=rows,
            columns=["document_id", "file_path", "content", "char_count"]
        )

    async def fetch(self, plan: ExecutionStep) -> NormalizedResult:
        # Offload intensive text/OCR processing to a background thread pool
        return await asyncio.to_thread(self._execute_sync, plan)