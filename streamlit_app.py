import streamlit as st
import os
import tempfile
from pathlib import Path
import json
from typing import Dict, Any

from legal_ai_system import legal_ai_system

# Page configuration
st.set_page_config(
    page_title="Legal AI Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">⚖️ Legal AI Assistant</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Upload & Process", "Search Documents", "System Stats", "Batch Processing"]
    )
    
    if page == "Upload & Process":
        upload_and_process_page()
    elif page == "Search Documents":
        search_documents_page()
    elif page == "System Stats":
        system_stats_page()
    elif page == "Batch Processing":
        batch_processing_page()

def upload_and_process_page():
    st.header("📄 Upload & Process Legal Documents")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a legal document in PDF format"
    )
    
    # Response type selection
    response_type = st.selectbox(
        "Response Type",
        ["professional", "formal", "conciliatory", "assertive"],
        help="Choose the tone for the generated response"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.info(f"📎 File: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        # Process button
        if st.button("🚀 Process Document & Generate Response", type="primary"):
            with st.spinner("Processing document..."):
                try:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    # Process the document
                    result = legal_ai_system.process_uploaded_pdf(tmp_file_path)
                    
                    # Clean up temp file
                    os.unlink(tmp_file_path)
                    
                    if result["success"]:
                        st.success("✅ Document processed successfully!")
                        
                        # Display document information
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("📋 Document Information")
                            st.write(f"**Document ID:** {result['document']['id']}")
                            st.write(f"**Type:** {result['document']['type']}")
                            st.write(f"**Parties:** {', '.join(result['document']['parties'])}")
                            st.write(f"**Key Issues:** {', '.join(result['document']['issues'])}")
                            st.write(f"**Chunks Created:** {result['chunks_created']}")
                        
                        with col2:
                            st.subheader("📊 Processing Stats")
                            st.write(f"**Status:** Success")
                            st.write(f"**Response Type:** {response_type}")
                            st.write(f"**Confidence:** {result['response']['confidence']:.2%}")
                        
                        # Display AI response
                        st.subheader("🤖 AI-Generated Response")
                        
                        # Response content
                        st.markdown("**Suggested Response:**")
                        st.text_area(
                            "Response",
                            value=result['response']['suggested_response'],
                            height=300,
                            disabled=True
                        )
                        
                        # Key points
                        if result['response']['key_points']:
                            st.markdown("**Key Points Addressed:**")
                            for i, point in enumerate(result['response']['key_points'], 1):
                                st.write(f"{i}. {point}")
                        
                        # Reasoning
                        if result['response']['reasoning']:
                            with st.expander("🔍 AI Reasoning"):
                                st.write(result['response']['reasoning'])
                        
                        # Download response
                        response_data = {
                            "document_id": result['document']['id'],
                            "response": result['response']['suggested_response'],
                            "confidence": result['response']['confidence'],
                            "key_points": result['response']['key_points'],
                            "reasoning": result['response']['reasoning']
                        }
                        
                        st.download_button(
                            label="📥 Download Response as JSON",
                            data=json.dumps(response_data, indent=2),
                            file_name=f"legal_response_{result['document']['id']}.json",
                            mime="application/json"
                        )
                        
                    else:
                        st.error(f"❌ Processing failed: {result['error']}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

def search_documents_page():
    st.header("🔍 Search Documents")
    
    # Search query
    query = st.text_input(
        "Enter your search query",
        placeholder="e.g., contract breach, employment dispute, intellectual property"
    )
    
    # Number of results
    n_results = st.slider("Number of results", 1, 20, 5)
    
    if st.button("🔍 Search", type="primary") and query:
        with st.spinner("Searching..."):
            try:
                results = legal_ai_system.search_similar_documents(query, n_results)
                
                if results:
                    st.success(f"✅ Found {len(results)} relevant documents")
                    
                    for i, result in enumerate(results, 1):
                        with st.expander(f"📄 {result['filename']} (Score: {result['similarity_score']:.2f})"):
                            st.write(f"**Document Type:** {result['document_type']}")
                            st.write(f"**Document ID:** {result['document_id']}")
                            
                            if result['relevant_chunks']:
                                st.write("**Relevant Content:**")
                                for j, chunk in enumerate(result['relevant_chunks'], 1):
                                    st.markdown(f"**Chunk {j}:**")
                                    st.text(chunk['content'][:300] + "..." if len(chunk['content']) > 300 else chunk['content'])
                                    st.write(f"*Similarity: {chunk['similarity']:.2f}*")
                                    st.divider()
                else:
                    st.info("No relevant documents found.")
                    
            except Exception as e:
                st.error(f"❌ Search error: {str(e)}")

def system_stats_page():
    st.header("📊 System Statistics")
    
    if st.button("🔄 Refresh Stats", type="primary"):
        with st.spinner("Loading statistics..."):
            try:
                stats = legal_ai_system.get_system_stats()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Total Chunks",
                        stats.get('vector_store', {}).get('total_chunks', 0)
                    )
                
                with col2:
                    st.metric(
                        "Model",
                        stats.get('model_name', 'Unknown')
                    )
                
                with col3:
                    st.metric(
                        "Collection",
                        stats.get('vector_store', {}).get('collection_name', 'Unknown')
                    )
                
                # Detailed stats
                st.subheader("📋 Detailed Information")
                st.json(stats)
                
            except Exception as e:
                st.error(f"❌ Error loading stats: {str(e)}")

def batch_processing_page():
    st.header("📦 Batch Processing")
    
    st.info("Upload multiple PDF files for batch processing")
    
    # Multiple file upload
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Select multiple PDF files for batch processing"
    )
    
    if uploaded_files:
        st.write(f"📎 Selected {len(uploaded_files)} files:")
        for file in uploaded_files:
            st.write(f"- {file.name} ({file.size} bytes)")
        
        if st.button("🚀 Process All Files", type="primary"):
            with st.spinner("Processing files..."):
                try:
                    results = []
                    
                    for uploaded_file in uploaded_files:
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name
                        
                        # Process the document
                        result = legal_ai_system.process_uploaded_pdf(tmp_file_path)
                        
                        # Clean up temp file
                        os.unlink(tmp_file_path)
                        
                        results.append({
                            "filename": uploaded_file.name,
                            "success": result["success"],
                            "document_id": result.get("document", {}).get("id") if result["success"] else None,
                            "error": result.get("error") if not result["success"] else None
                        })
                    
                    # Display results
                    successful = len([r for r in results if r["success"]])
                    failed = len(results) - successful
                    
                    st.success(f"✅ Batch processing complete! {successful} successful, {failed} failed")
                    
                    # Results table
                    st.subheader("📊 Processing Results")
                    
                    for result in results:
                        if result["success"]:
                            st.success(f"✅ {result['filename']} - ID: {result['document_id']}")
                        else:
                            st.error(f"❌ {result['filename']} - Error: {result['error']}")
                    
                    # Download results
                    st.download_button(
                        label="📥 Download Results as JSON",
                        data=json.dumps(results, indent=2),
                        file_name="batch_processing_results.json",
                        mime="application/json"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Batch processing error: {str(e)}")

if __name__ == "__main__":
    main() 
