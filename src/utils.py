"""Utility functions for NL2SQL Agent"""
import re
from typing import List, Dict, Any
from tabulate import tabulate


def extract_sql_query(text: str) -> str:
    """
    Extract SQL query from text that may contain markdown or other formatting.
    
    Args:
        text: Text potentially containing SQL query
        
    Returns:
        Extracted SQL query
    """
    # Remove markdown code blocks
    text = re.sub(r'```sql\n?', '', text)
    text = re.sub(r'```\n?', '', text)
    
    # Remove backticks
    text = text.replace('`', '')
    
    # Strip whitespace
    text = text.strip()
    
    return text


def validate_sql_safety(query: str) -> bool:
    """
    Validate that SQL query doesn't contain dangerous operations.
    
    Args:
        query: SQL query to validate
        
    Returns:
        True if query is safe, False otherwise
    """
    dangerous_patterns = [
        r'DROP\s+(?:TABLE|DATABASE)',
        r'DELETE\s+FROM',
        r'TRUNCATE',
        r'ALTER\s+TABLE',
        r'CREATE\s+(?:TABLE|DATABASE)',
        r'EXEC\(',
    ]
    
    query_upper = query.upper()
    
    for pattern in dangerous_patterns:
        if re.search(pattern, query_upper):
            return False
    
    return True


def format_results(
    results: List[Dict[str, Any]],
    max_rows: int = 20,
    tablefmt: str = "grid"
) -> str:
    """
    Format query results as a table.
    
    Args:
        results: List of result dictionaries
        max_rows: Maximum rows to display
        tablefmt: Table format (grid, simple, plain, etc.)
        
    Returns:
        Formatted table string
    """
    if not results:
        return "No results found."
    
    # Display only first max_rows
    displayed_results = results[:max_rows]
    
    # Create table
    table = tabulate(
        displayed_results,
        headers="keys",
        tablefmt=tablefmt
    )
    
    # Add info about truncation if needed
    if len(results) > max_rows:
        table += f"\n\n... and {len(results) - max_rows} more rows"
    
    return table


def print_agent_response(response: Dict[str, Any], show_query: bool = True):
    """
    Pretty print agent response.
    
    Args:
        response: Response dictionary from agent
        show_query: Whether to show the generated SQL query
    """
    print("\n" + "="*60)
    
    if response["status"] == "success":
        print(f"✅ Status: SUCCESS (Attempt {response['attempts']})")
        if show_query and response["query"]:
            print(f"\n📝 Generated Query:\n{response['query']}")
        
        print(f"\n📊 Results ({len(response['results'])} rows):\n")
        print(format_results(response["results"]))
    
    else:
        print(f"❌ Status: FAILED (Attempt {response['attempts']})")
        if show_query and response["query"]:
            print(f"\n📝 Generated Query:\n{response['query']}")
        
        if response["error"]:
            print(f"\n⚠️  Error: {response['error']}")
    
    print("\n" + "="*60 + "\n")
