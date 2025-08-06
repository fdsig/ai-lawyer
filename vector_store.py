import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import uuid
from sentence_transformers import SentenceTransformer
import numpy as np

from config import settings
from models import DocumentChunk, SearchResult

class ChromaVectorStore:
    """ChromaDB vector store for legal document chunks"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.chroma_db_path,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="legal_documents",
            metadata={"description": "Legal document chunks with embeddings"}
        )
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using sentence transformers"""
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()
    
    def add_chunks(self, chunks: List[DocumentChunk]) -> bool:
        """Add document chunks to vector store"""
        try:
            ids = []
            embeddings = []
            documents = []
            metadatas = []
            
            for chunk in chunks:
                # Generate embedding if not provided
                if chunk.embedding is None:
                    chunk.embedding = self._generate_embedding(chunk.content)
                
                ids.append(chunk.id)
                embeddings.append(chunk.embedding)
                documents.append(chunk.content)
                metadatas.append({
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "filename": chunk.metadata.get("filename", ""),
                    "document_type": chunk.metadata.get("document_type", ""),
                    **chunk.metadata
                })
            
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            return True
            
        except Exception as e:
            print(f"Error adding chunks to vector store: {e}")
            return False
    
    def search_similar(self, query: str, n_results: int = 5) -> List[SearchResult]:
        """Search for similar document chunks"""
        try:
            query_embedding = self._generate_embedding(query)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            search_results = []
            for i in range(len(results['ids'][0])):
                search_result = SearchResult(
                    chunk_id=results['ids'][0][i],
                    document_id=results['metadatas'][0][i]['document_id'],
                    content=results['documents'][0][i],
                    similarity_score=1 - results['distances'][0][i],  # Convert distance to similarity
                    metadata=results['metadatas'][0][i]
                )
                search_results.append(search_result)
            
            return search_results
            
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return []
    
    def get_document_chunks(self, document_id: str) -> List[SearchResult]:
        """Get all chunks for a specific document"""
        try:
            results = self.collection.get(
                where={"document_id": document_id},
                include=["documents", "metadatas"]
            )
            
            search_results = []
            for i in range(len(results['ids'])):
                search_result = SearchResult(
                    chunk_id=results['ids'][i],
                    document_id=results['metadatas'][i]['document_id'],
                    content=results['documents'][i],
                    similarity_score=1.0,  # Exact match
                    metadata=results['metadatas'][i]
                )
                search_results.append(search_result)
            
            return search_results
            
        except Exception as e:
            print(f"Error getting document chunks: {e}")
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """Delete all chunks for a specific document"""
        try:
            self.collection.delete(where={"document_id": document_id})
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection_name": self.collection.name
            }
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {"error": str(e)} 
