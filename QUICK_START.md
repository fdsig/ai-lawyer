# 🚀 Quick Start Guide

Get the Legal AI Assistant up and running in minutes!

## Prerequisites

- Python 3.8+
- OpenAI API key
- Git

## 1. Clone and Setup

```bash
git clone <repository-url>
cd ai-lawyer
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure API Key

```bash
cp env.example .env
# Edit .env and add your OpenAI API key
```

## 4. Start the System

### Option A: Easy Startup Script
```bash
./start.sh
```

### Option B: Manual Start
```bash
# Start Streamlit interface (recommended for beginners)
streamlit run streamlit_app.py

# Or start API server
python api.py
```

## 5. Access the Interface

- **Streamlit UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## 🎯 First Steps

1. **Upload a PDF**: Use the Streamlit interface to upload a legal document
2. **Process Document**: Click "Process Document & Generate Response"
3. **Review Results**: See the AI-generated response and analysis
4. **Search Documents**: Use the search feature to find similar cases

## 📋 What You Get

✅ **Document Processing**: Extract text and classify legal documents  
✅ **AI Analysis**: Identify parties, issues, and legal context  
✅ **Response Generation**: Professional legal responses with confidence scoring  
✅ **Vector Search**: Find similar documents and precedents  
✅ **RAG System**: Enhanced responses using relevant precedents  
✅ **Multi-Agent Framework**: Specialized AI agents for different tasks  

## 🔧 Advanced Usage

### API Endpoints
```bash
# Upload and process
curl -X POST "http://localhost:8000/upload-pdf" \
  -F "file=@document.pdf" \
  -F "response_type=professional"

# Search documents
curl "http://localhost:8000/search?query=contract+breach&n_results=5"

# Get system stats
curl "http://localhost:8000/stats"
```

### Programmatic Usage
```python
from legal_ai_system import legal_ai_system

# Process document
result = legal_ai_system.process_uploaded_pdf("document.pdf")

# Search similar documents
results = legal_ai_system.search_similar_documents("employment dispute")
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or use the startup script
./start.sh --docker
```

## 🆘 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure your API key is set in `.env`
   - Check that the key has sufficient credits

2. **Import Errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

3. **ChromaDB Issues**
   - Ensure `chroma_db` directory exists
   - Check disk space for vector storage

4. **Port Conflicts**
   - Change ports in `api.py` or `streamlit_app.py`
   - Check if ports 8000/8501 are already in use

### Getting Help

- Check the full [README.md](README.md) for detailed documentation
- Run `python example_usage.py` to see working examples
- Review API documentation at http://localhost:8000/docs

## 🎉 You're Ready!

Your Legal AI Assistant is now running! Start by uploading a legal document and see the AI in action.

---

**Need help?** Check the main [README.md](README.md) for comprehensive documentation. 
