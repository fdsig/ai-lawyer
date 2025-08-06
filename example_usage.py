#!/usr/bin/env python3
"""
Example usage of the Legal AI Assistant system.

This script demonstrates how to use the system programmatically
for processing legal documents and generating responses.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from legal_ai_system import legal_ai_system

def create_sample_legal_document():
    """Create a sample legal document for testing"""
    sample_content = """
    RE: Notice of Contract Breach
    
    Dear Mr. Smith,
    
    This letter serves as formal notice of breach of contract regarding the software development agreement dated January 15, 2024, between ABC Corporation ("Client") and XYZ Development LLC ("Contractor").
    
    Pursuant to Section 8.2 of the agreement, the Contractor has failed to deliver the completed software application by the agreed-upon deadline of March 1, 2024. This constitutes a material breach of the contract terms.
    
    The Client has suffered damages as a result of this breach, including:
    1. Loss of business opportunities due to delayed software deployment
    2. Additional costs incurred for temporary workarounds
    3. Reputational damage with our customers
    
    We demand immediate rectification of this breach and request a detailed plan for project completion within 30 days. Failure to comply may result in legal action to recover damages and terminate the agreement.
    
    Please contact our legal department within 10 business days to discuss resolution options.
    
    Sincerely,
    Jane Doe
    General Counsel
    ABC Corporation
    """
    
    # Create sample PDF file
    sample_file = Path("sample_legal_document.txt")
    with open(sample_file, "w") as f:
        f.write(sample_content)
    
    return str(sample_file)

def example_basic_usage():
    """Demonstrate basic usage of the legal AI system"""
    print("🚀 Legal AI Assistant - Basic Usage Example")
    print("=" * 50)
    
    # Create a sample document
    print("📄 Creating sample legal document...")
    sample_file = create_sample_legal_document()
    
    try:
        # Process the document
        print("🔍 Processing document...")
        result = legal_ai_system.process_uploaded_pdf(sample_file)
        
        if result["success"]:
            print("✅ Document processed successfully!")
            
            # Display document information
            print(f"\n📋 Document Information:")
            print(f"   ID: {result['document']['id']}")
            print(f"   Type: {result['document']['type']}")
            print(f"   Parties: {', '.join(result['document']['parties'])}")
            print(f"   Issues: {', '.join(result['document']['issues'])}")
            print(f"   Chunks: {result['chunks_created']}")
            
            # Display AI response
            if result['response']:
                print(f"\n🤖 AI-Generated Response:")
                print(f"   Confidence: {result['response']['confidence']:.2%}")
                print(f"   Response: {result['response']['suggested_response'][:200]}...")
                
                if result['response']['key_points']:
                    print(f"   Key Points: {', '.join(result['response']['key_points'])}")
        else:
            print(f"❌ Processing failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Clean up sample file
        if os.path.exists(sample_file):
            os.remove(sample_file)

def example_search_functionality():
    """Demonstrate search functionality"""
    print("\n🔍 Legal AI Assistant - Search Example")
    print("=" * 50)
    
    # Search for similar documents
    search_queries = [
        "contract breach",
        "employment dispute",
        "intellectual property",
        "payment default"
    ]
    
    for query in search_queries:
        print(f"\n🔎 Searching for: '{query}'")
        results = legal_ai_system.search_similar_documents(query, n_results=3)
        
        if results:
            print(f"   Found {len(results)} relevant documents:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['filename']} (Score: {result['similarity_score']:.2f})")
        else:
            print("   No relevant documents found.")

def example_system_stats():
    """Demonstrate system statistics"""
    print("\n📊 Legal AI Assistant - System Statistics")
    print("=" * 50)
    
    try:
        stats = legal_ai_system.get_system_stats()
        
        print("📈 System Overview:")
        print(f"   Total Chunks: {stats.get('vector_store', {}).get('total_chunks', 0)}")
        print(f"   Model: {stats.get('model_name', 'Unknown')}")
        print(f"   Collection: {stats.get('vector_store', {}).get('collection_name', 'Unknown')}")
        print(f"   Uploads Directory: {stats.get('uploads_directory', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")

def example_response_generation():
    """Demonstrate different response types"""
    print("\n🤖 Legal AI Assistant - Response Generation Example")
    print("=" * 50)
    
    # Get the first document from the system
    try:
        stats = legal_ai_system.get_system_stats()
        total_chunks = stats.get('vector_store', {}).get('total_chunks', 0)
        
        if total_chunks > 0:
            # This is a simplified example - in practice you'd need to know the document ID
            print("📝 Note: This example requires an existing document ID.")
            print("   Run the basic usage example first to create a document.")
            
            # Example response types
            response_types = ["professional", "formal", "conciliatory", "assertive"]
            print(f"   Available response types: {', '.join(response_types)}")
            
        else:
            print("📝 No documents in the system. Run the basic usage example first.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all examples"""
    print("⚖️ Legal AI Assistant - Example Usage")
    print("=" * 60)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set in environment variables.")
        print("   Please set your OpenAI API key before running examples.")
        print("   You can do this by:")
        print("   1. Creating a .env file with OPENAI_API_KEY=your_key")
        print("   2. Or setting the environment variable directly")
        return
    
    # Run examples
    example_basic_usage()
    example_search_functionality()
    example_system_stats()
    example_response_generation()
    
    print("\n🎉 Examples completed!")
    print("\n💡 Next steps:")
    print("   - Try the Streamlit interface: streamlit run streamlit_app.py")
    print("   - Start the API server: python api.py")
    print("   - Check the README.md for more detailed usage instructions")

if __name__ == "__main__":
    main() 
