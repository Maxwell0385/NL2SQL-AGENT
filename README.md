# NL2SQL Agent

A Natural Language to SQL conversion agent that translates English statements into SQL queries and executes them against a database.

## Features

- 🗣️ Convert natural language to SQL queries
- 🗄️ Support for multiple database types (SQLite, PostgreSQL, MySQL)
- 🔒 Safe query execution with validation
- 🎯 Iterative refinement on query failures
- 🌐 REST API and CLI interfaces
- 📊 Formatted result display

## Project Structure

```
nl2sql-agent/
├── src/
│   ├── agent.py           # Main NL2SQL agent logic
│   ├── database.py        # Database connection & execution
│   ├── llm.py            # LLM integration
│   └── utils.py          # Helper functions
├── examples/
│   ├── sample_db.sql     # Sample database setup
│   └── queries.txt       # Example natural language queries
├── tests/
│   └── test_agent.py     # Unit tests
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── main.py              # Entry point
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key (or LLaMA setup for local inference)
- SQLite/PostgreSQL/MySQL

### Installation

1. Clone the repository
```bash
git clone https://github.com/Maxwell0385/nl2sql-agent.git
cd nl2sql-agent
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
```bash
cp .env.example .env
# Add your API keys
```

4. Initialize sample database
```bash
python src/database.py --init
```

### Usage

#### CLI
```bash
python main.py "Show me all customers from New York who spent more than $1000"
```

#### Python API
```python
from src.agent import NL2SQLAgent

agent = NL2SQLAgent(db_config="config.json")
result = agent.query("What are the top 5 products by revenue?")
print(result)
```

#### REST API
```bash
python main.py --api
# POST http://localhost:8000/query
# {"query": "Show me all customers from New York"}
```

## How It Works

1. **Schema Understanding**: Agent reads database schema (tables, columns, relationships)
2. **Query Generation**: LLM generates SQL based on natural language input
3. **Validation**: Checks query for safety and correctness
4. **Execution**: Runs query against database
5. **Result Formatting**: Returns results in readable format
6. **Refinement**: If query fails, iteratively corrects based on error message

## Technologies

- **LLM**: OpenAI GPT-4, Claude, or LLaMA
- **Framework**: LangChain
- **Database**: SQLAlchemy (supports multiple DBs)
- **API**: FastAPI
- **CLI**: Click

## Example Queries

- "Show me all customers from New York who spent more than $1000"
- "What are the top 5 products by revenue this month?"
- "How many orders were placed in the last 7 days?"
- "List all employees earning more than $80,000"

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT
