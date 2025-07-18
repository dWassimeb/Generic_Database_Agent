"""
Streamlined Smart SQL Generator - PostgreSQL Support
"""

from typing import Dict, Any
from langchain.tools import BaseTool
from pydantic import Field
import logging
from llm.custom_gpt import CustomGPT
from config.schemas import TABLE_SCHEMAS, TABLE_RELATIONSHIPS

logger = logging.getLogger(__name__)

class SmartSqlGeneratorTool(BaseTool):
    """Streamlined SQL generator focused on accurate PostgreSQL queries."""

    name: str = "generate_smart_sql"
    description: str = "Generate optimal PostgreSQL queries from intent analysis efficiently."

    llm: CustomGPT = Field(default_factory=CustomGPT)

    def _run(self, user_question: str, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate PostgreSQL query from pre-analyzed intent."""
        try:
            # Validate input
            if not intent_analysis:
                raise ValueError("Intent analysis required for SQL generation")

            # Build focused context
            sql_context = self._build_sql_context(intent_analysis)

            # Generate SQL
            sql_query = self._generate_sql(user_question, sql_context, intent_analysis)

            # Validate and clean
            cleaned_sql = self._clean_sql(sql_query)

            # Extract metadata
            metadata = self._extract_metadata(cleaned_sql)

            return {
                'success': True,
                'sql_query': cleaned_sql,
                'sql_metadata': metadata,
                'message': "PostgreSQL query generated successfully"
            }

        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"SQL generation failed: {str(e)}"
            }

    def _build_sql_context(self, intent_analysis: Dict[str, Any]) -> str:
        """Build minimal SQL context based on intent."""

        # Get required tables
        table_analysis = intent_analysis.get('table_analysis', {})
        required_tables = table_analysis.get('required_tables', [])

        # Fallback to available tables if none specified
        if not required_tables:
            required_tables = list(TABLE_SCHEMAS.keys())[:2]  # Use first 2 tables as fallback

        context = "# PostgreSQL Database Context\n\n"

        # Only include relevant table schemas
        for table_name in required_tables:
            if table_name in TABLE_SCHEMAS:
                schema = TABLE_SCHEMAS[table_name]
                context += f"## {table_name}\n"
                context += f"Description: {schema.get('description', 'No description')}\n"

                # Essential columns only
                columns = schema.get('columns', {})
                for col_name, col_info in columns.items():
                    col_type = col_info.get('type', 'TEXT')
                    col_desc = col_info.get('description', 'No description')
                    context += f"- {col_name} ({col_type}): {col_desc}\n"
                context += "\n"

        # Add specific join patterns if needed
        join_analysis = intent_analysis.get('join_analysis', {})
        required_joins = join_analysis.get('required_joins', [])
        if required_joins:
            context += "# Required Joins:\n"
            for join in required_joins:
                context += f"- {join['from_table']} JOIN {join['to_table']} ON {join['join_condition']}\n"
            context += "\n"

        # Add PostgreSQL specifics
        context += """# PostgreSQL Functions:
- DATE_TRUNC('month', column) - Truncate to month
- TO_CHAR(date_column, 'YYYY-MM') - Format date as YYYY-MM
- TO_CHAR(date_column, 'YYYY-MM-DD') - Format date as YYYY-MM-DD
- EXTRACT(YEAR FROM date_column) - Extract year
- EXTRACT(MONTH FROM date_column) - Extract month
- NOW() - Current timestamp
- NOW() - INTERVAL '30 days' - Date arithmetic
- CURRENT_DATE - Current date only
- COUNT(*) - Count rows
- Percentage: (COUNT(*) * 100.0) / (SELECT COUNT(*) FROM table WHERE conditions)

# PostgreSQL Date/Time Examples:
- Monthly grouping: DATE_TRUNC('month', date_demande)
- Year filtering: EXTRACT(YEAR FROM date_demande) = 2025
- Month formatting: TO_CHAR(date_demande, 'YYYY-MM') as month
- Recent data: WHERE date_demande >= NOW() - INTERVAL '30 days'

# Critical Rules:
- Use PostgreSQL syntax (NOT SQLite or MySQL)
- NO strftime() function - use TO_CHAR() or DATE_TRUNC()
- Always include LIMIT clauses
- Use proper JOIN syntax
- Handle NULL values appropriately
- Use TIMESTAMP/DATE types correctly
"""

        return context

    def _generate_sql(self, user_question: str, sql_context: str, intent_analysis: Dict[str, Any]) -> str:
        """Generate PostgreSQL SQL with focused prompting."""

        # Build execution instructions
        instructions = self._build_instructions(intent_analysis)

        prompt = f"""Generate ONLY a PostgreSQL SQL query based on analyzed intent.

{sql_context}

## Analyzed Requirements:
{instructions}

## User Question: "{user_question}"

## PostgreSQL-Specific Guidelines:

### Common Query Patterns:
1. **Monthly Trends**: SELECT DATE_TRUNC('month', date_demande) as month, COUNT(*) FROM demandes GROUP BY DATE_TRUNC('month', date_demande) ORDER BY month
2. **Year Filtering**: WHERE EXTRACT(YEAR FROM date_demande) = 2025
3. **Recent Data**: WHERE date_demande >= NOW() - INTERVAL '30 days'
4. **Date Formatting**: TO_CHAR(date_demande, 'YYYY-MM') as formatted_month

### IMPORTANT - PostgreSQL Syntax Only:
- ✅ DATE_TRUNC('month', date_column)
- ✅ TO_CHAR(date_column, 'YYYY-MM')
- ✅ EXTRACT(YEAR FROM date_column)
- ✅ NOW() - INTERVAL '30 days'
- ❌ NO strftime() - this is SQLite only!
- ❌ NO date() function - use PostgreSQL functions

### For Time Series Queries:
- Use DATE_TRUNC('month', date_demande) for monthly grouping
- Use TO_CHAR(date_demande, 'YYYY-MM') for month labels
- Order by the date function used in GROUP BY

CRITICAL INSTRUCTIONS:
- Return ONLY the SQL query
- NO explanations, NO markdown, NO code blocks
- Start directly with SELECT
- End with semicolon
- Use PostgreSQL syntax only
- NEVER use SQLite functions like strftime()

PostgreSQL Query:"""

        try:
            response = self.llm._call(prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            raise

    def _build_instructions(self, intent_analysis: Dict[str, Any]) -> str:
        """Build concise execution instructions."""
        instructions = []

        # Tables
        table_analysis = intent_analysis.get('table_analysis', {})
        if table_analysis.get('required_tables'):
            instructions.append(f"Tables: {', '.join(table_analysis['required_tables'])}")

        # Joins
        join_analysis = intent_analysis.get('join_analysis', {})
        if join_analysis.get('required_joins'):
            join_count = len(join_analysis['required_joins'])
            instructions.append(f"Joins: {join_count} required")

        # Columns
        column_analysis = intent_analysis.get('column_analysis', {})
        if column_analysis.get('aggregation_needed'):
            instructions.append("Aggregation: Required")
        if column_analysis.get('grouping_columns'):
            instructions.append(f"Group by: {', '.join(column_analysis['grouping_columns'])}")

        # Time filters
        temporal_analysis = intent_analysis.get('temporal_analysis', {})
        if temporal_analysis.get('needs_time_filter'):
            period = temporal_analysis.get('time_period', '7 days')
            instructions.append(f"Time filter: Last {period}")

        # Output
        output_req = intent_analysis.get('output_requirements', {})
        if output_req.get('needs_percentage'):
            instructions.append("Calculate: Percentages")
        if output_req.get('suggested_limit'):
            instructions.append(f"Limit: {output_req['suggested_limit']}")

        return "\n".join([f"- {inst}" for inst in instructions])

    def _clean_sql(self, sql_query: str) -> str:
        """Clean and validate SQL - Enhanced version."""
        original_query = sql_query

        # Step 1: Remove markdown code blocks
        if '```' in sql_query:
            # Split by ``` and find the SQL part
            parts = sql_query.split('```')
            for part in parts:
                part = part.strip()
                # Skip empty parts and language identifiers
                if not part or part.lower() in ['sql', 'postgresql', '']:
                    continue
                # Look for SELECT statements
                if 'SELECT' in part.upper():
                    sql_query = part
                    break

        # Step 2: Remove language identifiers at the start
        lines = sql_query.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            # Skip empty lines and language identifiers
            if not line or line.lower() in ['sql', 'postgresql', 'postgres']:
                continue
            # Stop at explanations or markdown
            if line.startswith('#') or line.lower().startswith('explanation'):
                break
            cleaned_lines.append(line)

        sql_query = '\n'.join(cleaned_lines)

        # Step 3: Remove trailing content after semicolon
        if ';' in sql_query:
            sql_query = sql_query.split(';')[0] + ';'

        # Step 4: Clean up whitespace
        sql_query = sql_query.strip().rstrip(';').strip()

        # Step 5: Handle empty or malformed queries
        if not sql_query:
            raise ValueError("Generated query is empty after cleaning")

        # Step 6: Basic validation
        sql_upper = sql_query.upper()
        if not sql_upper.startswith('SELECT'):
            # Try to find SELECT in the query
            if 'SELECT' in sql_upper:
                # Extract from SELECT onwards
                select_index = sql_upper.find('SELECT')
                sql_query = sql_query[select_index:]
                sql_upper = sql_query.upper()
            else:
                raise ValueError(f"Query must be a SELECT statement. Got: {sql_query[:100]}...")

        # Step 7: Check for dangerous keywords
        dangerous = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
        for keyword in dangerous:
            if keyword in sql_upper:
                raise ValueError(f"Dangerous keyword detected: {keyword}")

        # Step 8: Check for SQLite functions that should be PostgreSQL
        if 'STRFTIME' in sql_upper:
            raise ValueError("SQLite strftime() function detected - use PostgreSQL TO_CHAR() or DATE_TRUNC()")

        logger.info(f"Cleaned SQL query: {sql_query}")
        return sql_query

    def _extract_metadata(self, sql_query: str) -> Dict[str, Any]:
        """Extract basic metadata from SQL."""
        sql_upper = sql_query.upper()

        metadata = {
            'query_type': 'SELECT',
            'estimated_complexity': 'simple',
            'tables_used': [],
            'has_joins': 'JOIN' in sql_upper,
            'has_aggregation': any(agg in sql_upper for agg in ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX']),
            'has_time_filter': any(time_func in sql_upper for time_func in ['DATE_TRUNC', 'TO_CHAR', 'EXTRACT', 'NOW()', 'INTERVAL']),
            'aggregations_used': []
        }

        # Extract table names (simple heuristic)
        if 'FROM' in sql_upper:
            from_part = sql_query.split('FROM')[1].split('WHERE')[0] if 'WHERE' in sql_query else sql_query.split('FROM')[1]
            for table_name in TABLE_SCHEMAS.keys():
                if table_name.upper() in from_part.upper():
                    metadata['tables_used'].append(table_name)

        # Extract aggregations
        agg_functions = ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX']
        for agg in agg_functions:
            if agg in sql_upper:
                metadata['aggregations_used'].append(agg)

        # Estimate complexity
        complexity_score = 0
        if metadata['has_joins']:
            complexity_score += 2
        if metadata['has_aggregation']:
            complexity_score += 1
        if len(metadata['tables_used']) > 1:
            complexity_score += 1
        if metadata['has_time_filter']:
            complexity_score += 1

        if complexity_score >= 4:
            metadata['estimated_complexity'] = 'complex'
        elif complexity_score >= 2:
            metadata['estimated_complexity'] = 'moderate'

        return metadata