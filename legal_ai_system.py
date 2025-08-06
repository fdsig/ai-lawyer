import os
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path

from config import settings
from models import LegalDocument, LegalResponse, ProcessingResult
from document_processor import DocumentProcessor
from vector_store import ChromaVectorStore
from legal_agents import LegalAgentSystem

class LegalAISystem:
    """Main legal AI system for document processing and response generation"""
    
    def __init__(self):
        """Initialize the legal AI system with all components"""
        self.vector_store = ChromaVectorStore()
        self.document_processor = DocumentProcessor()
        self.agent_system = LegalAgentSystem(self.vector_store)
        
        # Create uploads directory
        self.uploads_dir = Path("uploads")
        self.uploads_dir.mkdir(exist_ok=True)
    
    def process_and_store_pdf(self, pdf_path: str, filename: Optional[str] = None) -> ProcessingResult:
        """Process a PDF file and store it in the vector database"""
        try:
            if filename is None:
                filename = os.path.basename(pdf_path)
            
            # Process the PDF
            result = self.document_processor.process_pdf(pdf_path, filename)
            
            if not result.success:
                return result
            
            # Store chunks in vector database
            if result.chunks:
                storage_success = self.vector_store.add_chunks(result.chunks)
                if not storage_success:
                    result.success = False
                    result.error_message = "Failed to store document in vector database"
            
            return result
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                error_message=str(e)
            )
    
    def generate_response_for_document(self, document_id: str, response_type: str = "professional") -> Optional[LegalResponse]:
        """Generate a legal response for a specific document"""
        try:
            # Get document chunks from vector store
            chunks = self.vector_store.get_document_chunks(document_id)
            
            if not chunks:
                print(f"No document found with ID: {document_id}")
                return None
            
            # Reconstruct document content
            content = "\n".join([chunk.content for chunk in chunks])
            
            # Get metadata from first chunk
            metadata = chunks[0].metadata
            
            # Create document object
            document = LegalDocument(
                id=document_id,
                filename=metadata.get("filename", "Unknown"),
                content=content,
                document_type=metadata.get("document_type", "legal_letter"),
                parties_involved=metadata.get("parties_involved", []),
                key_issues=metadata.get("key_issues", []),
                metadata=metadata
            )
            
            # Generate response
            response = self.agent_system.generate_legal_response(document, response_type)
            return response
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return None
    
    def search_similar_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents in the knowledge base"""
        try:
            results = self.vector_store.search_similar(query, n_results)
            
            # Group results by document
            document_results = {}
            for result in results:
                doc_id = result.document_id
                if doc_id not in document_results:
                    document_results[doc_id] = {
                        "document_id": doc_id,
                        "filename": result.metadata.get("filename", "Unknown"),
                        "document_type": result.metadata.get("document_type", "Unknown"),
                        "similarity_score": result.similarity_score,
                        "relevant_chunks": []
                    }
                
                document_results[doc_id]["relevant_chunks"].append({
                    "content": result.content,
                    "similarity": result.similarity_score
                })
            
            return list(document_results.values())
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            vector_stats = self.vector_store.get_collection_stats()
            
            return {
                "vector_store": vector_stats,
                "uploads_directory": str(self.uploads_dir),
                "model_name": settings.model_name
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def process_uploaded_pdf(self, file_path: str) -> Dict[str, Any]:
        """Process an uploaded PDF file and generate a response"""
        try:
            # Process and store the PDF
            result = self.process_and_store_pdf(file_path)
            
            if not result.success:
                return {
                    "success": False,
                    "error": result.error_message
                }
            
            # Generate response
            response = self.generate_response_for_document(result.document.id)
            
            return {
                "success": True,
                "document": {
                    "id": result.document.id,
                    "filename": result.document.filename,
                    "type": result.document.document_type.value,
                    "parties": result.document.parties_involved,
                    "issues": result.document.key_issues
                },
                "response": {
                    "suggested_response": response.suggested_response if response else "No response generated",
                    "confidence": response.confidence_score if response else 0.0,
                    "key_points": response.key_points if response else [],
                    "reasoning": response.reasoning if response else ""
                } if response else None,
                "chunks_created": len(result.chunks)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def batch_process_pdfs(self, pdf_paths: List[str]) -> List[Dict[str, Any]]:
        """Process multiple PDF files in batch"""
        results = []
        
        for pdf_path in pdf_paths:
            try:
                result = self.process_and_store_pdf(pdf_path)
                results.append({
                    "file": pdf_path,
                    "success": result.success,
                    "document_id": result.document.id if result.document else None,
                    "error": result.error_message if not result.success else None
                })
            except Exception as e:
                results.append({
                    "file": pdf_path,
                    "success": False,
                    "error": str(e)
                })
        
        return results

# Global system instance
legal_ai_system = LegalAISystem() 
