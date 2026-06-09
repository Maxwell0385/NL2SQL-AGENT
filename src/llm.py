"""LLM Integration Module"""
import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()


class NL2SQLLLMAgent:
    """LLM Agent for converting natural language to SQL"""

    def __init__(self, model: str = "gpt-4", temperature: float = 0.0):
        """
        Initialize the LLM agent.
        
        Args:
            model: Model name (default: gpt-4)
            temperature: Model temperature for generation
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=temperature
        )
        
        self.sql_generation_prompt = PromptTemplate(
            input_variables=["schema", "question"],
            template="""
            You are an expert SQL query generator. Convert the following natural language question 
            into a valid SQL query.
            
            Database Schema:
            {schema}
            
            Question: {question}
            
            Generate ONLY the SQL query, without any explanation or markdown formatting.
            The query should be valid and safe.
            """
        )
        
        self.error_refinement_prompt = PromptTemplate(
            input_variables=["schema", "question", "previous_query", "error_message"],
            template="""
            The following SQL query failed with an error. Please fix it and generate a corrected query.
            
            Database Schema:
            {schema}
            
            Original Question: {question}
            
            Previous Query: {previous_query}
            
            Error: {error_message}
            
            Generate ONLY the corrected SQL query, without any explanation or markdown formatting.
            """
        )

    def generate_sql(self, schema: str, question: str) -> str:
        """
        Generate SQL query from natural language question.
        
        Args:
            schema: Database schema description
            question: Natural language question
            
        Returns:
            Generated SQL query
        """
        prompt = self.sql_generation_prompt.format(schema=schema, question=question)
        response = self.llm.invoke(prompt)
        return response.content.strip()

    def refine_sql(self, schema: str, question: str, previous_query: str, error_message: str) -> str:
        """
        Refine SQL query based on error message.
        
        Args:
            schema: Database schema description
            question: Original natural language question
            previous_query: Previously generated query that failed
            error_message: Error message from query execution
            
        Returns:
            Refined SQL query
        """
        prompt = self.error_refinement_prompt.format(
            schema=schema,
            question=question,
            previous_query=previous_query,
            error_message=error_message
        )
        response = self.llm.invoke(prompt)
        return response.content.strip()
