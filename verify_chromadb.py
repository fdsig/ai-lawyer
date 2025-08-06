#!/usr/bin/env python3
"""
Simple script to verify ChromaDB contents
"""

from vector_store import ChromaVectorStore
import json

def main():
    print("🔍 ChromaDB Verification")
    print("=" * 30)
    
    vector_store = ChromaVectorStore()
    
    # Get collection stats
    stats = vector_store.get_collection_stats()
    print(f"📊 Collection Stats: {stats}")
    
    # Get all documents
    all_results = vector_store.collection.get()
    
    if not all_results['ids']:
        print("📭 No documents found in ChromaDB")
        return
    
    print(f"\n📄 Found {len(all_results['ids'])} chunks:")
    
    for i, (chunk_id, content, metadata) in enumerate(zip(all_results['ids'], all_results['documents'], all_results['metadatas']), 1):
        print(f"\n{i}. Chunk ID: {chunk_id}")
        print(f"   Document: {metadata.get('filename', 'Unknown')}")
        print(f"   Document ID: {metadata.get('document_id', 'Unknown')}")
        print(f"   Chunk Index: {metadata.get('chunk_index', 'Unknown')}")
        print(f"   Document Type: {metadata.get('document_type', 'Unknown')}")
        print(f"   Content Preview: {content[:100]}...")
        
        # Show all metadata
        print(f"   All Metadata: {json.dumps(metadata, indent=2)}")
    
    # Test search functionality
    print(f"\n🔍 Testing search functionality...")
    search_results = vector_store.search_similar("payment demand", n_results=2)
    
    if search_results:
        print(f"✅ Search found {len(search_results)} results:")
        for i, result in enumerate(search_results, 1):
            print(f"   {i}. Document: {result.metadata.get('filename', 'Unknown')}")
            print(f"      Relevance: {result.similarity_score:.2f}")
            print(f"      Content: {result.content[:80]}...")
    else:
        print("❌ No search results found")

if __name__ == "__main__":
    main() 
