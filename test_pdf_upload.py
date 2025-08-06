#!/usr/bin/env python3
"""
Test script to verify PDF upload and ChromaDB storage functionality
"""

import os
import tempfile
import json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from legal_ai_system import legal_ai_system
from vector_store import ChromaVectorStore
from document_processor import DocumentProcessor

def create_sample_legal_pdf(filepath: str) -> str:
    """Create a sample legal document PDF for testing"""
    
    # Sample legal content
    legal_content = """
    LEGAL NOTICE AND DEMAND FOR PAYMENT
    
    Date: August 6, 2025
    
    To: John Smith
    Address: 123 Main Street, Anytown, CA 90210
    
    From: ABC Corporation
    Address: 456 Business Ave, Corporate City, CA 90211
    
    Subject: Outstanding Invoice Payment - Invoice #INV-2025-001
    
    Dear Mr. Smith,
    
    This letter serves as formal notice regarding the outstanding balance of $5,000.00 
    for services rendered by ABC Corporation pursuant to our service agreement dated 
    January 15, 2025.
    
    According to our records, the following amounts remain unpaid:
    
    - Invoice #INV-2025-001: $5,000.00 (Due Date: March 15, 2025)
    - Late fees (30 days): $250.00
    - Total Outstanding: $5,250.00
    
    Despite our previous communications and payment reminders, we have not received 
    payment for these outstanding amounts. This constitutes a breach of our service 
    agreement and may result in legal action if payment is not received within 30 days 
    of this notice.
    
    LEGAL RIGHTS AND REMEDIES:
    
    Pursuant to California Civil Code Section 1719, we reserve the right to:
    1. Pursue legal action for breach of contract
    2. Seek recovery of attorney's fees and court costs
    3. Report this delinquency to credit reporting agencies
    4. Engage collection services if necessary
    
    PAYMENT OPTIONS:
    
    To avoid further legal action, please remit payment in full within 30 days to:
    
    ABC Corporation
    P.O. Box 789
    Corporate City, CA 90211
    
    Or make payment online at: www.abccorp.com/payment
    
    If you have any questions regarding this matter, please contact our legal 
    department at legal@abccorp.com or (555) 123-4567.
    
    Sincerely,
    
    Jane Doe
    Legal Department
    ABC Corporation
    
    This communication is from a debt collector attempting to collect a debt.
    """
    
    # Create PDF
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    
    # Set font and size
    c.setFont("Helvetica", 12)
    
    # Split content into lines and add to PDF
    lines = legal_content.split('\n')
    y_position = height - 50  # Start from top with margin
    
    for line in lines:
        if line.strip():  # Skip empty lines
            c.drawString(50, y_position, line.strip())
            y_position -= 15  # Move down for next line
        
        # Add new page if we're running out of space
        if y_position < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = height - 50
    
    c.save()
    return filepath

def test_pdf_upload_and_storage():
    """Test the complete PDF upload and storage pipeline"""
    
    print("🧪 Testing PDF Upload and ChromaDB Storage")
    print("=" * 50)
    
    # Step 1: Create a sample PDF
    print("📄 Creating sample legal PDF...")
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        pdf_path = create_sample_legal_pdf(tmp_file.name)
    
    try:
        # Step 2: Test document processing
        print("🔍 Testing document processing...")
        processor = DocumentProcessor()
        result = processor.process_pdf(pdf_path, "test_legal_notice.pdf")
        
        if not result.success:
            print(f"❌ Document processing failed: {result.error_message}")
            return False
        
        print(f"✅ Document processed successfully!")
        print(f"   - Document ID: {result.document.id}")
        print(f"   - Filename: {result.document.filename}")
        print(f"   - Document Type: {result.document.document_type}")
        print(f"   - Parties Involved: {result.document.parties_involved}")
        print(f"   - Key Issues: {result.document.key_issues}")
        print(f"   - Chunks Created: {len(result.chunks)}")
        
        # Step 3: Test vector store storage
        print("\n🗄️  Testing ChromaDB storage...")
        vector_store = ChromaVectorStore()
        storage_success = vector_store.add_chunks(result.chunks)
        
        if not storage_success:
            print("❌ Failed to store chunks in ChromaDB")
            return False
        
        print("✅ Chunks stored successfully in ChromaDB!")
        
        # Step 4: Verify storage by searching
        print("\n🔍 Verifying storage with search...")
        search_results = vector_store.search_similar("payment demand legal notice", n_results=3)
        
        if search_results:
            print(f"✅ Found {len(search_results)} relevant chunks:")
            for i, result in enumerate(search_results, 1):
                print(f"   {i}. Document: {result.metadata.get('filename', 'Unknown')}")
                print(f"      Relevance: {result.similarity_score:.2f}")
                print(f"      Content: {result.content[:100]}...")
        else:
            print("❌ No search results found - storage may have failed")
            return False
        
        # Step 5: Test full system integration
        print("\n🤖 Testing full system integration...")
        system_result = legal_ai_system.process_uploaded_pdf(pdf_path)
        
        if system_result["success"]:
            print("✅ Full system integration successful!")
            print(f"   - Document ID: {system_result['document']['id']}")
            print(f"   - Response generated: {system_result['response'] is not None}")
            if system_result['response']:
                print(f"   - Confidence: {system_result['response']['confidence']:.2%}")
        else:
            print(f"❌ System integration failed: {system_result.get('error', 'Unknown error')}")
            return False
        
        # Step 6: Get system stats
        print("\n📊 System Statistics:")
        stats = legal_ai_system.get_system_stats()
        print(f"   - Total chunks in vector store: {stats.get('vector_store', {}).get('total_chunks', 0)}")
        print(f"   - Collection name: {stats.get('vector_store', {}).get('collection_name', 'Unknown')}")
        print(f"   - Model: {stats.get('model_name', 'Unknown')}")
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False
    
    finally:
        # Clean up temporary file
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)

def test_chromadb_direct_operations():
    """Test direct ChromaDB operations"""
    
    print("\n🔧 Testing Direct ChromaDB Operations")
    print("=" * 40)
    
    try:
        vector_store = ChromaVectorStore()
        
        # Test collection stats
        stats = vector_store.get_collection_stats()
        print(f"✅ Collection stats: {stats}")
        
        # Test document retrieval
        print("\n📋 Testing document retrieval...")
        # Get all documents (this will be empty initially)
        all_results = vector_store.collection.get()
        print(f"   - Total documents in collection: {len(all_results['ids']) if all_results['ids'] else 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    
    print("🚀 Starting PDF Upload and ChromaDB Storage Tests")
    print("=" * 60)
    
    # Test 1: Direct ChromaDB operations
    chromadb_success = test_chromadb_direct_operations()
    
    # Test 2: Full PDF upload and storage pipeline
    upload_success = test_pdf_upload_and_storage()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"ChromaDB Operations: {'✅ PASSED' if chromadb_success else '❌ FAILED'}")
    print(f"PDF Upload Pipeline: {'✅ PASSED' if upload_success else '❌ FAILED'}")
    
    if chromadb_success and upload_success:
        print("\n🎉 ALL TESTS PASSED! PDF upload and ChromaDB storage is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 
