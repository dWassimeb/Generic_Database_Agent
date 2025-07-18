"""
Query execution tool with PostgreSQL database support.
"""

from typing import Dict, Any, List
from langchain.tools import BaseTool
import re
import logging

# Import from new database location
from src.database.connection import database_connection

logger = logging.getLogger(__name__)

class QueryExecutionTool(BaseTool):
    """Tool for executing SQL queries safely on PostgreSQL database."""

    name: str = "execute_query"
    description: str = """
    Execute SQL queries on PostgreSQL database safely.
    Validates queries, adds safety limits, and returns structured results.
    """

    def _run(self, sql_query: str) -> Dict[str, Any]:
        """Execute the SQL query safely."""
        try:
            # Validate query safety
            if not self._validate_query(sql_query):
                return {
                    'success': False,
                    'error': 'Query validation failed - potentially unsafe query',
                    'details': 'Only SELECT statements are allowed'
                }

            # Add safety limits
            safe_query = self._add_safety_limits(sql_query)

            # Execute the query
            result = database_connection.execute_query_with_names(safe_query)

            # Process results
            processed_result = self._process_results(result)

            return {
                'success': True,
                'result': processed_result,
                'executed_query': safe_query,
                'message': f"Query executed successfully"
            }

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            error_info = self._parse_sql_error(str(e))
            return {
                'success': False,
                'error': error_info['user_message'],
                'suggestion': error_info['suggestion'],
                'details': str(e)
            }

    def _validate_query(self, query: str) -> bool:
        """Validate SQL query for security and safety."""
        # Remove comments and normalize whitespace
        clean_query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        clean_query = ' '.join(clean_query.split())
        clean_query = clean_query.upper()

        # Check for dangerous operations
        dangerous_keywords = [
            'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
            'TRUNCATE', 'REPLACE', 'EXEC', 'EXECUTE'
        ]

        for keyword in dangerous_keywords:
            if keyword in clean_query:
                logger.warning(f"Dangerous keyword '{keyword}' found in query")
                return False

        # Ensure query starts with SELECT
        if not clean_query.strip().startswith('SELECT'):
            logger.warning("Query does not start with SELECT")
            return False

        return True

    def _add_safety_limits(self, query: str, default_limit: int = 1000) -> str:
        """Add LIMIT clause if not present."""
        query_upper = query.upper()

        # Check if LIMIT already exists
        if 'LIMIT' in query_upper:
            return query

        # Add LIMIT clause
        return f"{query.rstrip(';')} LIMIT {default_limit}"

    def _process_results(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process and format query results."""
        if not result.get('data'):
            return {
                'columns': result.get('columns', []),
                'data': [],
                'row_count': 0,
                'message': 'Query executed successfully but returned no data'
            }

        return {
            'columns': result.get('columns', []),
            'data': result.get('data', []),
            'types': result.get('types', []),
            'row_count': result.get('row_count', len(result.get('data', []))),
            'message': f"Retrieved {result.get('row_count', 0)} rows successfully"
        }

    def _parse_sql_error(self, error_str: str) -> Dict[str, str]:
        """Parse SQL error and provide user-friendly messages."""
        error_lower = error_str.lower()

        if 'syntax error' in error_lower:
            return {
                'user_message': 'SQL syntax error in the generated query',
                'suggestion': 'Please rephrase your question or try a simpler request'
            }
        elif 'table' in error_lower and 'does not exist' in error_lower:
            return {
                'user_message': 'Referenced table does not exist in the database',
                'suggestion': 'Ask for available tables first with "list tables" or "show tables"'
            }
        elif 'column' in error_lower and 'does not exist' in error_lower:
            return {
                'user_message': 'Referenced column does not exist',
                'suggestion': 'Check the table structure or ask for table schema information'
            }
        elif 'connection' in error_lower:
            return {
                'user_message': 'Database connection error',
                'suggestion': 'Please check if the database server is running and accessible'
            }
        else:
            return {
                'user_message': 'Database query error occurred',
                'suggestion': 'Please try rephrasing your question or contact support'
            }