import pypdf
from typing import List, Dict, Any, Optional
import uuid
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from config import settings
from models import LegalDocument, DocumentChunk, DocumentType, ProcessingResult

class DocumentProcessor:
    """Process legal documents and extract structured information"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.model_name,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            api_key=settings.openai_api_key
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {e}")
    
    def classify_document_type(self, content: str) -> DocumentType:
        """Classify the type of legal document using LLM"""
        try:
            classification_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a legal document classifier. Analyze the content and classify it into one of these categories:
                - legal_letter: General legal correspondence
                - contract: Legal agreements, contracts, terms
                - notice: Legal notices, warnings, formal announcements
                - complaint: Legal complaints, grievances
                - response: Legal responses, replies, counter-arguments
                
                Respond with only the category name."""),
                ("human", "Classify this legal document:\n\n{content}")
            ])
            
            response = self.llm.invoke(
                classification_prompt.format_messages(content=content[:2000])
            )
            
            doc_type_str = response.content.strip().lower()
            
            # Map response to enum
            type_mapping = {
                "legal_letter": DocumentType.LEGAL_LETTER,
                "contract": DocumentType.CONTRACT,
                "notice": DocumentType.NOTICE,
                "complaint": DocumentType.COMPLAINT,
                "response": DocumentType.RESPONSE
            }
            
            return type_mapping.get(doc_type_str, DocumentType.LEGAL_LETTER)
            
        except Exception as e:
            print(f"Error classifying document: {e}")
            return DocumentType.LEGAL_LETTER
    
    def extract_parties_and_issues(self, content: str) -> tuple[List[str], List[str]]:
        """Extract parties involved and key legal issues using LLM"""
        try:
            extraction_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a legal document analyzer. Extract:
                1. Parties involved (names of people, companies, organizations)
                2. Key legal issues mentioned
                
                Format your response as:
                PARTIES: [comma-separated list]
                ISSUES: [comma-separated list]"""),
                ("human", "Analyze this legal document:\n\n{content}")
            ])
            
            response = self.llm.invoke(
                extraction_prompt.format_messages(content=content[:2000])
            )
            
            response_text = response.content
            
            # Parse response
            parties = []
            issues = []
            
            if "PARTIES:" in response_text:
                parties_section = response_text.split("PARTIES:")[1].split("ISSUES:")[0]
                parties = [p.strip() for p in parties_section.strip().split(",") if p.strip()]
            
            if "ISSUES:" in response_text:
                issues_section = response_text.split("ISSUES:")[1]
                issues = [i.strip() for i in issues_section.strip().split(",") if i.strip()]
            
            return parties, issues
            
        except Exception as e:
            print(f"Error extracting parties and issues: {e}")
            return [], []
    
    def create_chunks(self, content: str, document_id: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Create chunks from document content"""
        try:
            # Split text into chunks
            text_chunks = self.text_splitter.split_text(content)
            
            chunks = []
            for i, chunk_text in enumerate(text_chunks):
                chunk = DocumentChunk(
                    id=str(uuid.uuid4()),
                    document_id=document_id,
                    content=chunk_text,
                    chunk_index=i,
                    metadata=metadata
                )
                chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            print(f"Error creating chunks: {e}")
            return []
    
    def process_pdf(self, pdf_path: str, filename: str) -> ProcessingResult:
        """Process a PDF file and return structured document with chunks"""
        try:
            # Extract text
            content = self.extract_text_from_pdf(pdf_path)
            
            if not content.strip():
                return ProcessingResult(
                    success=False,
                    error_message="No text content extracted from PDF"
                )
            
            # Generate document ID
            document_id = str(uuid.uuid4())
            
            # Classify document type
            document_type = self.classify_document_type(content)
            
            # Extract parties and issues
            parties, issues = self.extract_parties_and_issues(content)
            
            # Create document
            document = LegalDocument(
                id=document_id,
                filename=filename,
                content=content,
                document_type=document_type,
                parties_involved=parties,
                key_issues=issues,
                metadata={
                    "source_file": pdf_path,
                    "word_count": len(content.split()),
                    "pages": len(content.split('\n\n'))
                }
            )
            
            # Create chunks
            chunk_metadata = {
                "filename": filename,
                "document_type": document_type.value,
                "parties_involved": parties,
                "key_issues": issues
            }
            
            chunks = self.create_chunks(content, document_id, chunk_metadata)
            
            return ProcessingResult(
                success=True,
                document=document,
                chunks=chunks
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                error_message=str(e)
            ) 
