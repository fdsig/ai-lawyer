from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    LEGAL_LETTER = "legal_letter"
    CONTRACT = "contract"
    NOTICE = "notice"
    COMPLAINT = "complaint"
    RESPONSE = "response"

class LegalDocument(BaseModel):
    """Model for legal document structure"""
    id: str = Field(description="Unique document identifier")
    filename: str = Field(description="Original filename")
    content: str = Field(description="Extracted text content")
    document_type: DocumentType = Field(description="Type of legal document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.now)
    parties_involved: List[str] = Field(default_factory=list, description="Parties mentioned in document")
    key_issues: List[str] = Field(default_factory=list, description="Key legal issues identified")
    
class LegalResponse(BaseModel):
    """Model for AI-generated legal response"""
    document_id: str = Field(description="Reference to original document")
    response_type: str = Field(description="Type of response (acknowledgment, counter, etc.)")
    suggested_response: str = Field(description="AI-generated response text")
    confidence_score: float = Field(description="Confidence in the response quality", ge=0.0, le=1.0)
    reasoning: str = Field(description="AI reasoning for the response")
    key_points: List[str] = Field(description="Key points addressed in response")
    tone: str = Field(description="Professional tone of response")
    created_at: datetime = Field(default_factory=datetime.now)

class DocumentChunk(BaseModel):
    """Model for document chunks stored in vector DB"""
    id: str = Field(description="Unique chunk identifier")
    document_id: str = Field(description="Parent document ID")
    content: str = Field(description="Chunk content")
    chunk_index: int = Field(description="Position in document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")
    embedding: Optional[List[float]] = Field(default=None, description="Vector embedding")

class SearchResult(BaseModel):
    """Model for search results from vector DB"""
    chunk_id: str = Field(description="Chunk identifier")
    document_id: str = Field(description="Parent document ID")
    content: str = Field(description="Chunk content")
    similarity_score: float = Field(description="Similarity score")
    metadata: Dict[str, Any] = Field(description="Chunk metadata")

class ProcessingResult(BaseModel):
    """Model for document processing results"""
    success: bool = Field(description="Processing success status")
    document: Optional[LegalDocument] = Field(default=None, description="Processed document")
    chunks: List[DocumentChunk] = Field(default_factory=list, description="Generated chunks")
    error_message: Optional[str] = Field(default=None, description="Error message if failed") 
