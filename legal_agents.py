from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import uuid

from config import settings
from models import LegalDocument, LegalResponse, SearchResult
from vector_store import ChromaVectorStore

class LegalAnalysisTool(BaseTool):
    """Tool for analyzing legal documents and extracting key information"""
    
    name: str = "legal_analysis"
    description: str = "Analyze legal documents to extract key legal issues, parties, and context"
    
    def _run(self, document_content: str) -> str:
        """Run the legal analysis tool"""
        llm = ChatOpenAI(
            model=settings.model_name,
            temperature=0.1,
            api_key=settings.openai_api_key
        )
        
        analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a legal analyst. Analyze the provided legal document and extract:
            1. Key legal issues and arguments
            2. Parties involved and their positions
            3. Relevant legal precedents or citations
            4. Potential legal risks or concerns
            5. Recommended response strategy
            
            Provide a structured analysis."""),
            ("human", "Analyze this legal document:\n\n{document_content}")
        ])
        
        response = llm.invoke(
            analysis_prompt.format_messages(document_content=document_content[:3000])
        )
        
        return response.content

class PrecedentSearchTool(BaseTool):
    """Tool for searching similar legal precedents"""
    
    name: str = "precedent_search"
    description: str = "Search for similar legal cases and precedents in the knowledge base"
    vector_store: ChromaVectorStore
    
    def __init__(self, vector_store: ChromaVectorStore):
        super().__init__(vector_store=vector_store)
    
    def _run(self, query: str) -> str:
        """Search for similar precedents"""
        results = self.vector_store.search_similar(query, n_results=3)
        
        if not results:
            return "No similar precedents found in the knowledge base."
        
        precedent_text = "Similar precedents found:\n\n"
        for i, result in enumerate(results, 1):
            precedent_text += f"{i}. Document: {result.metadata.get('filename', 'Unknown')}\n"
            precedent_text += f"   Relevance: {result.similarity_score:.2f}\n"
            precedent_text += f"   Content: {result.content[:200]}...\n\n"
        
        return precedent_text

class ResponseGeneratorTool(BaseTool):
    """Tool for generating legal responses"""
    
    name: str = "response_generator"
    description: str = "Generate professional legal responses based on analysis and precedents"
    
    def _run(self, analysis: str, precedents: str, response_type: str = "professional") -> str:
        """Generate a legal response"""
        llm = ChatOpenAI(
            model=settings.model_name,
            temperature=0.3,
            api_key=settings.openai_api_key
        )
        
        response_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a legal response generator. Create a professional legal response based on:
            1. The legal analysis provided
            2. Similar precedents and cases
            3. The requested response type
            
            The response should be:
            - Professional and legally sound
            - Address all key issues raised
            - Reference relevant precedents when appropriate
            - Maintain appropriate tone for the situation
            - Include clear next steps or recommendations"""),
            ("human", """Generate a legal response with the following information:
            
            Analysis: {analysis}
            
            Precedents: {precedents}
            
            Response Type: {response_type}
            
            Please provide a comprehensive legal response.""")
        ])
        
        response = llm.invoke(
            response_prompt.format_messages(
                analysis=analysis,
                precedents=precedents,
                response_type=response_type
            )
        )
        
        return response.content

class LegalAgentSystem:
    """Multi-agent system for legal document processing and response generation"""
    
    def __init__(self, vector_store: ChromaVectorStore):
        self.vector_store = vector_store
        self.llm = ChatOpenAI(
            model=settings.model_name,
            temperature=settings.temperature,
            api_key=settings.openai_api_key
        )
        
        # Initialize tools
        self.analysis_tool = LegalAnalysisTool()
        self.precedent_tool = PrecedentSearchTool(vector_store)
        self.response_tool = ResponseGeneratorTool()
        
        # Create agent
        tools = [self.analysis_tool, self.precedent_tool, self.response_tool]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a legal assistant agent system. Your role is to:
            1. Analyze incoming legal documents
            2. Search for relevant precedents
            3. Generate appropriate legal responses
            
            Use the available tools to perform these tasks effectively.
            Always provide professional, legally sound advice."""),
            ("human", "{input}"),
            ("ai", "{agent_scratchpad}")
        ])
        
        self.agent = create_openai_functions_agent(self.llm, tools, prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=tools, verbose=True)
    
    def generate_legal_response(self, document: LegalDocument, response_type: str = "professional") -> LegalResponse:
        """Generate a comprehensive legal response for a document"""
        try:
            # Step 1: Analyze the document
            analysis = self.analysis_tool._run(document.content)
            
            # Step 2: Search for precedents
            search_query = f"legal issues: {', '.join(document.key_issues)} parties: {', '.join(document.parties_involved)}"
            precedents = self.precedent_tool._run(search_query)
            
            # Step 3: Generate response
            suggested_response = self.response_tool._run(analysis, precedents, response_type)
            
            # Step 4: Evaluate confidence and extract key points
            confidence_analysis = self._evaluate_response_quality(suggested_response, document)
            
            # Create response object
            legal_response = LegalResponse(
                document_id=document.id,
                response_type=response_type,
                suggested_response=suggested_response,
                confidence_score=confidence_analysis["confidence"],
                reasoning=confidence_analysis["reasoning"],
                key_points=confidence_analysis["key_points"],
                tone=response_type
            )
            
            return legal_response
            
        except Exception as e:
            print(f"Error generating legal response: {e}")
            return LegalResponse(
                document_id=document.id,
                response_type=response_type,
                suggested_response="Error generating response. Please try again.",
                confidence_score=0.0,
                reasoning="Error occurred during response generation",
                key_points=[],
                tone="error"
            )
    
    def _evaluate_response_quality(self, response: str, document: LegalDocument) -> Dict[str, Any]:
        """Evaluate the quality and confidence of the generated response"""
        try:
            evaluation_prompt = ChatPromptTemplate.from_messages([
                ("system", """Evaluate the quality of a legal response. Provide:
                1. Confidence score (0.0 to 1.0)
                2. Reasoning for the score
                3. Key points addressed in the response
                
                Format as:
                CONFIDENCE: [score]
                REASONING: [explanation]
                KEY_POINTS: [comma-separated list]"""),
                ("human", """Evaluate this legal response for the document:
                
                Document Issues: {issues}
                Document Parties: {parties}
                
                Response: {response}""")
            ])
            
            evaluation = self.llm.invoke(
                evaluation_prompt.format_messages(
                    issues=", ".join(document.key_issues),
                    parties=", ".join(document.parties_involved),
                    response=response
                )
            )
            
            # Parse evaluation
            eval_text = evaluation.content
            confidence = 0.5  # Default
            reasoning = "Standard evaluation"
            key_points = []
            
            if "CONFIDENCE:" in eval_text:
                try:
                    conf_section = eval_text.split("CONFIDENCE:")[1].split("REASONING:")[0]
                    confidence = float(conf_section.strip())
                except:
                    pass
            
            if "REASONING:" in eval_text:
                reasoning_section = eval_text.split("REASONING:")[1].split("KEY_POINTS:")[0]
                reasoning = reasoning_section.strip()
            
            if "KEY_POINTS:" in eval_text:
                points_section = eval_text.split("KEY_POINTS:")[1]
                key_points = [p.strip() for p in points_section.strip().split(",") if p.strip()]
            
            return {
                "confidence": confidence,
                "reasoning": reasoning,
                "key_points": key_points
            }
            
        except Exception as e:
            print(f"Error evaluating response quality: {e}")
            return {
                "confidence": 0.5,
                "reasoning": "Evaluation failed",
                "key_points": []
            }
    
    def process_document_and_respond(self, document: LegalDocument) -> LegalResponse:
        """Complete pipeline: process document and generate response"""
        return self.generate_legal_response(document) 
