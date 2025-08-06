from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from pathlib import Path
from typing import List, Optional
import uuid

from legal_ai_system import legal_ai_system
from models import LegalResponse

app = FastAPI(
    title="Legal AI Assistant",
    description="AI-powered legal document processing and response generation system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Legal AI Assistant API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        stats = legal_ai_system.get_system_stats()
        return {
            "status": "healthy",
            "system_stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System error: {str(e)}")

@app.post("/upload-pdf")
async def upload_and_process_pdf(
    file: UploadFile = File(...),
    response_type: str = Form("professional")
):
    """Upload and process a PDF document"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Create unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"
        file_path = legal_ai_system.uploads_dir / filename
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the PDF
        result = legal_ai_system.process_uploaded_pdf(str(file_path))
        
        if not result["success"]:
            # Clean up file on error
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/process-pdf")
async def process_existing_pdf(
    file_path: str = Form(...),
    response_type: str = Form("professional")
):
    """Process an existing PDF file"""
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        result = legal_ai_system.process_uploaded_pdf(file_path)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/generate-response")
async def generate_response(
    document_id: str = Form(...),
    response_type: str = Form("professional")
):
    """Generate a legal response for a specific document"""
    try:
        response = legal_ai_system.generate_response_for_document(document_id, response_type)
        
        if response is None:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "success": True,
            "response": {
                "document_id": response.document_id,
                "response_type": response.response_type,
                "suggested_response": response.suggested_response,
                "confidence_score": response.confidence_score,
                "reasoning": response.reasoning,
                "key_points": response.key_points,
                "tone": response.tone,
                "created_at": response.created_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response generation error: {str(e)}")

@app.get("/search")
async def search_documents(
    query: str,
    n_results: int = 5
):
    """Search for similar documents"""
    try:
        results = legal_ai_system.search_similar_documents(query, n_results)
        
        return {
            "success": True,
            "query": query,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/document/{document_id}")
async def get_document_info(document_id: str):
    """Get information about a specific document"""
    try:
        chunks = legal_ai_system.vector_store.get_document_chunks(document_id)
        
        if not chunks:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get metadata from first chunk
        metadata = chunks[0].metadata
        
        return {
            "success": True,
            "document": {
                "id": document_id,
                "filename": metadata.get("filename", "Unknown"),
                "document_type": metadata.get("document_type", "Unknown"),
                "parties_involved": metadata.get("parties_involved", []),
                "key_issues": metadata.get("key_issues", []),
                "chunks_count": len(chunks)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document retrieval error: {str(e)}")

@app.delete("/document/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the system"""
    try:
        success = legal_ai_system.vector_store.delete_document(document_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "success": True,
            "message": f"Document {document_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion error: {str(e)}")

@app.get("/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        stats = legal_ai_system.get_system_stats()
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval error: {str(e)}")

@app.post("/batch-process")
async def batch_process_pdfs(file_paths: List[str]):
    """Process multiple PDF files in batch"""
    try:
        results = legal_ai_system.batch_process_pdfs(file_paths)
        
        return {
            "success": True,
            "results": results,
            "total_files": len(file_paths),
            "successful": len([r for r in results if r["success"]])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
