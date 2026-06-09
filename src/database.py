"""Database Module"""
import os
import sqlite3
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, inspect, MetaData, text
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    """Manages database connections and operations"""

    def __init__(self, db_type: str = "sqlite", **kwargs):
        """
        Initialize database manager.
        
        Args:
            db_type: Type of database (sqlite, postgresql, mysql)
            **kwargs: Additional database configuration
        """
        self.db_type = db_type
        self.connection_string = self._build_connection_string(db_type, kwargs)
        self.engine = create_engine(self.connection_string)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)

    def _build_connection_string(self, db_type: str, config: Dict) -> str:
        """
        Build database connection string.
        
        Args:
            db_type: Type of database
            config: Configuration dictionary
            
        Returns:
            Connection string
        """
        if db_type == "sqlite":
            db_path = config.get("db_path", "./data/sample.db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            return f"sqlite:///{db_path}"
        elif db_type == "postgresql":
            user = config.get("user", "postgres")
            password = config.get("password", "")
            host = config.get("host", "localhost")
            port = config.get("port", 5432)
            database = config.get("database", "nl2sql_db")
            return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        elif db_type == "mysql":
            user = config.get("user", "root")
            password = config.get("password", "")
            host = config.get("host", "localhost")
            port = config.get("port", 3306)
            database = config.get("database", "nl2sql_db")
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def get_schema_description(self) -> str:
        """
        Get a formatted description of the database schema.
        
        Returns:
            Schema description string
        """
        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        
        schema_description = "Database Schema:\n\n"
        
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            schema_description += f"Table: {table_name}\n"
            schema_description += "Columns:\n"
            
            for column in columns:
                col_type = str(column['type'])
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                schema_description += f"  - {column['name']}: {col_type} {nullable}\n"
            
            # Get foreign keys
            fks = inspector.get_foreign_keys(table_name)
            if fks:
                schema_description += "Foreign Keys:\n"
                for fk in fks:
                    schema_description += f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}\n"
            
            schema_description += "\n"
        
        return schema_description

    def execute_query(self, query: str) -> tuple[List[Dict[str, Any]], Optional[str]]:
        """
        Execute a SQL query safely.
        
        Args:
            query: SQL query to execute
            
        Returns:
            Tuple of (results, error_message)
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                
                # Handle SELECT queries
                if result.returns_rows:
                    columns = result.keys()
                    rows = result.fetchall()
                    results = [dict(zip(columns, row)) for row in rows]
                    return results, None
                else:
                    # Handle INSERT, UPDATE, DELETE queries
                    return [{"rows_affected": result.rowcount}], None
        
        except Exception as e:
            error_message = str(e)
            return [], error_message

    def initialize_sample_database(self):
        """
        Initialize sample database with test data.
        """
        sample_schema = """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            city TEXT,
            country TEXT,
            total_spent REAL
        );
        
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock INTEGER
        );
        
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER,
            order_date TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
        """
        
        sample_data = """
        INSERT OR IGNORE INTO customers VALUES 
        (1, 'John Doe', 'john@example.com', 'New York', 'USA', 5000),
        (2, 'Jane Smith', 'jane@example.com', 'New York', 'USA', 8500),
        (3, 'Bob Johnson', 'bob@example.com', 'Los Angeles', 'USA', 2000),
        (4, 'Alice Brown', 'alice@example.com', 'Chicago', 'USA', 3500),
        (5, 'Charlie Wilson', 'charlie@example.com', 'New York', 'USA', 6200);
        
        INSERT OR IGNORE INTO products VALUES
        (1, 'Laptop', 'Electronics', 1200, 50),
        (2, 'Mouse', 'Electronics', 25, 200),
        (3, 'Keyboard', 'Electronics', 75, 150),
        (4, 'Monitor', 'Electronics', 300, 80),
        (5, 'Desk Chair', 'Furniture', 200, 40);
        
        INSERT OR IGNORE INTO orders VALUES
        (1, 1, 1, 1, '2024-01-15'),
        (2, 1, 2, 2, '2024-01-16'),
        (3, 2, 1, 1, '2024-01-20'),
        (4, 2, 4, 1, '2024-01-22'),
        (5, 3, 3, 1, '2024-02-01'),
        (6, 4, 2, 3, '2024-02-05'),
        (7, 5, 5, 2, '2024-02-10');
        """
        
        with self.engine.connect() as connection:
            connection.execute(text(sample_schema))
            connection.execute(text(sample_data))
            connection.commit()
        
        print("Sample database initialized successfully!")
