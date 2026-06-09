"""Unit tests for NL2SQL Agent"""
import pytest
from src.agent import NL2SQLAgent
from src.database import DatabaseManager
from src.utils import extract_sql_query, validate_sql_safety


class TestUtils:
    """Test utility functions"""
    
    def test_extract_sql_query(self):
        """Test SQL query extraction from formatted text"""
        text = "```sql\nSELECT * FROM customers;\n```"
        result = extract_sql_query(text)
        assert "SELECT" in result
        assert "FROM" in result
    
    def test_validate_sql_safety_safe(self):
        """Test that safe queries pass validation"""
        query = "SELECT * FROM customers WHERE city = 'New York'"
        assert validate_sql_safety(query) is True
    
    def test_validate_sql_safety_dangerous(self):
        """Test that dangerous queries fail validation"""
        queries = [
            "DROP TABLE customers",
            "DELETE FROM customers",
            "TRUNCATE TABLE customers",
        ]
        for query in queries:
            assert validate_sql_safety(query) is False


class TestDatabaseManager:
    """Test database manager"""
    
    @pytest.fixture
    def db_manager(self):
        """Create test database manager"""
        return DatabaseManager(
            db_type="sqlite",
            db_path=":memory:"
        )
    
    def test_connection_string_sqlite(self):
        """Test SQLite connection string generation"""
        manager = DatabaseManager(db_type="sqlite", db_path="test.db")
        assert "sqlite:///test.db" in manager.connection_string


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
