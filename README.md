# ⚖️ Legal AI Assistant

A comprehensive AI-powered legal document processing and response generation system built with LangChain, Pydantic AI, multi-agent frameworks, and ChromaDB.

## 🚀 Features

### Core Capabilities
- **PDF Document Processing**: Extract and analyze legal documents from PDF files
- **Intelligent Document Classification**: Automatically classify legal documents (letters, contracts, notices, complaints, responses)
- **Multi-Agent Response Generation**: AI agents analyze documents and generate professional legal responses
- **Vector Database Storage**: Store document chunks in ChromaDB for semantic search and retrieval
- **RAG (Retrieval-Augmented Generation)**: Use similar precedents to enhance response quality
- **Professional Response Types**: Generate responses with different tones (professional, formal, conciliatory, assertive)

### Technical Stack
- **LangChain**: LLM orchestration and document processing
- **Pydantic AI**: Structured data models and validation
- **ChromaDB**: Vector database for document storage and similarity search
- **Multi-Agent Framework**: Specialized AI agents for legal analysis and response generation
- **FastAPI**: RESTful API for system integration
- **Streamlit**: User-friendly web interface
- **Azure OpenAI**: LLM backend (configurable)

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- 4GB+ RAM (for embedding models)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-lawyer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your OpenAI API key
   ```

4. **Create necessary directories**
   ```bash
   mkdir uploads
   mkdir chroma_db
   ```

## ⚙️ Configuration

Edit the `.env` file with your settings:

```env
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_DB_PATH=./chroma_db
MODEL_NAME=gpt-4
TEMPERATURE=0.1
MAX_TOKENS=2000
```

## 🚀 Usage

### Web Interface (Recommended)

Start the Streamlit web interface:

```bash
streamlit run streamlit_app.py
```

Navigate to `http://localhost:8501` to access the user-friendly interface.

### API Server

Start the FastAPI server:

```bash
python api.py
```

The API will be available at `http://localhost:8000` with automatic documentation at `http://localhost:8000/docs`.

### Command Line Usage

```python
from legal_ai_system import legal_ai_system

# Process a PDF and generate response
result = legal_ai_system.process_uploaded_pdf("path/to/legal_document.pdf")

# Search for similar documents
results = legal_ai_system.search_similar_documents("contract breach dispute")

# Get system statistics
stats = legal_ai_system.get_system_stats()
```

## 📖 API Endpoints

### Document Processing
- `POST /upload-pdf` - Upload and process a PDF document
- `POST /process-pdf` - Process an existing PDF file
- `POST /batch-process` - Process multiple PDF files

### Response Generation
- `POST /generate-response` - Generate legal response for a document

### Search & Retrieval
- `GET /search` - Search for similar documents
- `GET /document/{document_id}` - Get document information
- `DELETE /document/{document_id}` - Delete a document

### System Management
- `GET /health` - Health check
- `GET /stats` - System statistics

## 🏗️ Architecture

### Core Components

1. **Document Processor** (`document_processor.py`)
   - PDF text extraction
   - Document classification using LLM
   - Party and issue extraction
   - Text chunking for vector storage

2. **Vector Store** (`vector_store.py`)
   - ChromaDB integration
   - Document chunk storage
   - Semantic similarity search
   - Embedding generation

3. **Multi-Agent System** (`legal_agents.py`)
   - Legal analysis agent
   - Precedent search agent
   - Response generation agent
   - Quality evaluation

4. **Main System** (`legal_ai_system.py`)
   - Orchestrates all components
   - Handles document processing pipeline
   - Manages system state

### Data Models

- `LegalDocument`: Structured legal document representation
- `LegalResponse`: AI-generated response with confidence scoring
- `DocumentChunk`: Vector database storage unit
- `SearchResult`: Similarity search results

## 🔧 Advanced Usage

### Custom Response Types

```python
# Generate different types of responses
response = legal_ai_system.generate_response_for_document(
    document_id="doc_123",
    response_type="assertive"  # Options: professional, formal, conciliatory, assertive
)
```

### Batch Processing

```python
# Process multiple documents
pdf_paths = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
results = legal_ai_system.batch_process_pdfs(pdf_paths)
```

### Custom Search

```python
# Search with custom parameters
results = legal_ai_system.search_similar_documents(
    query="employment contract termination",
    n_results=10
)
```

## 📊 System Statistics

Monitor your system with built-in statistics:

```python
stats = legal_ai_system.get_system_stats()
print(f"Total chunks: {stats['vector_store']['total_chunks']}")
print(f"Model: {stats['model_name']}")
```

## 🔒 Security & Privacy

- All document processing happens locally
- Vector database stored locally
- No data sent to external services except OpenAI API
- Temporary files automatically cleaned up
- Configurable data retention policies

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "api.py"]
```

### Production Considerations

- Use environment variables for sensitive configuration
- Implement proper logging and monitoring
- Set up backup for ChromaDB data
- Configure rate limiting for API endpoints
- Use HTTPS in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information

## 🔮 Future Enhancements

- [ ] OCR support for scanned documents
- [ ] Multi-language support
- [ ] Integration with legal databases
- [ ] Advanced document comparison
- [ ] Automated legal research
- [ ] Compliance checking
- [ ] Document summarization
- [ ] Risk assessment scoring

---

**Built with ❤️ for the legal community**
