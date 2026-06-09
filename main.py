#!/usr/bin/env python
"""Main entry point for NL2SQL Agent"""
import os
import sys
import click
from src.agent import NL2SQLAgent
from src.database import DatabaseManager
from src.utils import print_agent_response
from dotenv import load_dotenv

load_dotenv()


@click.group()
def cli():
    """NL2SQL Agent CLI"""
    pass


@cli.command()
@click.argument('query', required=False)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--show-query', is_flag=True, default=True, help='Show generated SQL query')
def query(query: str, verbose: bool, show_query: bool):
    """
    Query the database using natural language.
    
    Example: python main.py query "Show me all customers from New York"
    """
    if not query:
        query = click.prompt("Enter your query")
    
    # Initialize agent
    db_config = {
        "db_path": os.getenv("DB_PATH", "./data/sample.db")
    }
    
    agent = NL2SQLAgent(
        db_type=os.getenv("DB_TYPE", "sqlite"),
        llm_model=os.getenv("OPENAI_MODEL", "gpt-4"),
        **db_config
    )
    
    # Execute query
    response = agent.query(query, verbose=verbose)
    
    # Print results
    print_agent_response(response, show_query=show_query)


@cli.command()
def init_db():
    """
    Initialize sample database with test data.
    """
    click.echo("Initializing sample database...")
    
    db_config = {
        "db_path": os.getenv("DB_PATH", "./data/sample.db")
    }
    
    db = DatabaseManager(
        db_type=os.getenv("DB_TYPE", "sqlite"),
        **db_config
    )
    
    db.initialize_sample_database()
    click.echo("✅ Database initialized!")


@cli.command()
def schema():
    """
    Display the database schema.
    """
    db_config = {
        "db_path": os.getenv("DB_PATH", "./data/sample.db")
    }
    
    db = DatabaseManager(
        db_type=os.getenv("DB_TYPE", "sqlite"),
        **db_config
    )
    
    schema_description = db.get_schema_description()
    print("\n" + "="*60)
    print("DATABASE SCHEMA")
    print("="*60 + "\n")
    print(schema_description)


@cli.command()
@click.option('--host', default='0.0.0.0', help='API host')
@click.option('--port', default=8000, help='API port')
def api(host: str, port: int):
    """
    Start REST API server.
    """
    try:
        import uvicorn
        from fastapi import FastAPI
        from pydantic import BaseModel
        
        app = FastAPI(title="NL2SQL Agent API")
        
        class QueryRequest(BaseModel):
            query: str
            verbose: bool = False
        
        class QueryResponse(BaseModel):
            status: str
            query: str
            results: list
            error: str = None
            attempts: int
        
        # Initialize agent
        db_config = {
            "db_path": os.getenv("DB_PATH", "./data/sample.db")
        }
        
        agent = NL2SQLAgent(
            db_type=os.getenv("DB_TYPE", "sqlite"),
            llm_model=os.getenv("OPENAI_MODEL", "gpt-4"),
            **db_config
        )
        
        @app.post("/query", response_model=QueryResponse)
        def process_query(request: QueryRequest):
            """Process natural language query"""
            response = agent.query(request.query, verbose=request.verbose)
            return QueryResponse(**response)
        
        @app.get("/schema")
        def get_schema():
            """Get database schema"""
            return {"schema": agent.schema}
        
        @app.get("/health")
        def health():
            """Health check"""
            return {"status": "healthy"}
        
        click.echo(f"🚀 Starting API server at http://{host}:{port}")
        click.echo(f"📚 API docs available at http://{host}:{port}/docs")
        
        uvicorn.run(app, host=host, port=port)
    
    except ImportError:
        click.echo("Error: fastapi and uvicorn are required for API mode")
        click.echo("Install with: pip install fastapi uvicorn")
        sys.exit(1)


if __name__ == "__main__":
    cli()
