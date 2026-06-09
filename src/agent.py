"""Main NL2SQL Agent Module"""
from typing import List, Dict, Any, Optional
from src.llm import NL2SQLLLMAgent
from src.database import DatabaseManager
from src.utils import extract_sql_query, validate_sql_safety


class NL2SQLAgent:
    """Main agent for converting natural language to SQL and executing queries"""

    def __init__(
        self,
        db_type: str = "sqlite",
        llm_model: str = "gpt-4",
        max_retries: int = 3,
        **db_config
    ):
        """
        Initialize the NL2SQL Agent.
        
        Args:
            db_type: Type of database
            llm_model: LLM model to use
            max_retries: Maximum retry attempts for query refinement
            **db_config: Database configuration
        """
        self.db = DatabaseManager(db_type=db_type, **db_config)
        self.llm = NL2SQLLLMAgent(model=llm_model)
        self.max_retries = max_retries
        self.schema = self.db.get_schema_description()

    def query(
        self,
        natural_language_query: str,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Convert natural language query to SQL and execute it.
        
        Args:
            natural_language_query: User's natural language question
            verbose: Print debug information
            
        Returns:
            Dictionary with results, query, and status
        """
        results = {
            "status": "error",
            "query": None,
            "results": [],
            "error": None,
            "attempts": 0
        }
        
        if verbose:
            print(f"\n🔍 Processing query: {natural_language_query}")
        
        # Generate initial SQL query
        if verbose:
            print("📝 Generating SQL query...")
        
        sql_query = self.llm.generate_sql(self.schema, natural_language_query)
        sql_query = extract_sql_query(sql_query)
        
        if verbose:
            print(f"Generated SQL: {sql_query}")
        
        # Validate SQL safety
        if not validate_sql_safety(sql_query):
            results["error"] = "Query contains potentially dangerous operations"
            return results
        
        # Execute query with retry logic
        for attempt in range(self.max_retries):
            results["attempts"] = attempt + 1
            results["query"] = sql_query
            
            if verbose:
                print(f"\n🚀 Executing query (Attempt {attempt + 1}/{self.max_retries})...")
            
            query_results, error = self.db.execute_query(sql_query)
            
            if error is None:
                results["status"] = "success"
                results["results"] = query_results
                if verbose:
                    print(f"✅ Query executed successfully! Retrieved {len(query_results)} rows.")
                return results
            
            else:
                if verbose:
                    print(f"❌ Query failed: {error}")
                
                # Try to refine the query
                if attempt < self.max_retries - 1:
                    if verbose:
                        print(f"🔧 Refining query based on error...")
                    
                    sql_query = self.llm.refine_sql(
                        self.schema,
                        natural_language_query,
                        sql_query,
                        error
                    )
                    sql_query = extract_sql_query(sql_query)
                    
                    if verbose:
                        print(f"Refined SQL: {sql_query}")
                else:
                    results["error"] = error
                    if verbose:
                        print(f"❌ Failed after {self.max_retries} attempts")
        
        return results
