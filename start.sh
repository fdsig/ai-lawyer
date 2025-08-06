#!/bin/bash

# Legal AI Assistant Startup Script

echo "⚖️  Legal AI Assistant - Starting up..."
echo "======================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "📝 Please edit .env file with your OpenAI API key"
        echo "   Then run this script again."
        exit 1
    else
        echo "❌ env.example not found. Please create .env file manually."
        exit 1
    fi
fi

# Load environment variables
source .env

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ OpenAI API key not set in .env file"
    echo "   Please edit .env and add your OpenAI API key"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads chroma_db

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "🐳 Running in Docker container"
    echo "🚀 Starting API server..."
    python api.py
else
    # Check if user wants to use Docker
    if [ "$1" = "--docker" ]; then
        echo "🐳 Starting with Docker Compose..."
        docker-compose up --build
    else
        echo "💻 Starting locally..."
        echo ""
        echo "Choose an option:"
        echo "1. Start API server (FastAPI)"
        echo "2. Start Streamlit interface"
        echo "3. Run example usage"
        echo "4. Start both API and Streamlit"
        echo ""
        read -p "Enter your choice (1-4): " choice
        
        case $choice in
            1)
                echo "🚀 Starting API server..."
                python api.py
                ;;
            2)
                echo "🚀 Starting Streamlit interface..."
                streamlit run streamlit_app.py
                ;;
            3)
                echo "🚀 Running example usage..."
                python example_usage.py
                ;;
            4)
                echo "🚀 Starting both services..."
                echo "   API will be available at http://localhost:8000"
                echo "   Streamlit will be available at http://localhost:8501"
                echo ""
                echo "Starting API in background..."
                python api.py &
                API_PID=$!
                echo "API started with PID: $API_PID"
                echo ""
                echo "Starting Streamlit..."
                streamlit run streamlit_app.py
                echo ""
                echo "Stopping API server..."
                kill $API_PID
                ;;
            *)
                echo "❌ Invalid choice"
                exit 1
                ;;
        esac
    fi
fi 
