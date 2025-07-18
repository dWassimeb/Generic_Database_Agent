"""
Streamlined Smart Intent Analyzer - Essential functionality only
"""

from typing import Dict, Any
from langchain.tools import BaseTool
from pydantic import Field
import json
import logging
from llm.custom_gpt import CustomGPT
from config.schemas import TABLE_SCHEMAS, TABLE_RELATIONSHIPS, BUSINESS_SCENARIOS

logger = logging.getLogger(__name__)

class SmartIntentAnalyzerTool(BaseTool):
    """Streamlined LLM-powered intent analyzer for semantic understanding."""

    name: str = "analyze_intent"
    description: str = "Analyze user intent and map to database concepts efficiently."

    llm: CustomGPT = Field(default_factory=CustomGPT)

    def _run(self, user_question: str) -> Dict[str, Any]:
        """Perform streamlined semantic analysis of user question."""
        try:
            # Build focused schema context (only essential info)
            schema_context = self._build_focused_context()

            # Get LLM analysis
            llm_analysis = self._get_semantic_analysis(user_question, schema_context)

            # Parse and validate
            parsed_analysis = self._parse_analysis(llm_analysis)
            validated_analysis = self._validate_analysis(parsed_analysis)

            return {
                'success': True,
                'user_question': user_question,
                **validated_analysis,
                'message': "Intent analysis completed"
            }

        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Intent analysis failed: {str(e)}"
            }

    def _build_focused_context(self) -> str:
        """Build minimal but complete schema context."""
        context = "# SQL Database Schema\n\n"

        # Essential table info only
        for table_name, schema in TABLE_SCHEMAS.items():
            context += f"## {table_name}\n"
            context += f"Purpose: {schema.get('description', '')}\n"
            context += f"Key columns: "

            # Only show most important columns
            key_columns = []
            for col_name, col_info in schema.get('columns', {}).items():
                if (col_info.get('is_primary_key') or
                    col_info.get('foreign_key') or
                    col_info.get('is_geographic') or
                    col_info.get('is_temporal') or
                    'NAME' in col_name.upper() or
                    'ID' in col_name.upper()):
                    key_columns.append(f"{col_name} ({col_info['type']})")

            context += ", ".join(key_columns[:5]) + "\n\n"

        # Essential relationships
        context += "# Key Relationships\n"
        for table_name, relationships in TABLE_RELATIONSHIPS.items():
            if relationships.get('joins_to'):
                for target_table, join_info in relationships['joins_to'].items():
                    context += f"- {table_name} → {target_table} (via {join_info.get('join_key', 'unknown')})\n"
        context += "\n"

        return context

    def _get_semantic_analysis(self, user_question: str, schema_context: str) -> str:
        """Get focused LLM analysis with chart type detection."""

        prompt = f"""Analyze this database query and provide a structured JSON response.

{schema_context}

User Question: "{user_question}"

## CHART TYPE DETECTION:
Detect if the user explicitly requested a specific chart/graph type:

**Keywords to detect:**
- "line chart", "line graph", "courbe", "évolution" → line
- "bar chart", "bar graph", "barres", "histogram" → bar  
- "horizontal bar", "ranking", "top" → horizontal_bar
- "pie chart", "camembert", "secteurs", "répartition" → pie
- "donut", "doughnut", "anneau" → doughnut
- "scatter plot", "nuage de points", "corrélation" → scatter
- "radar", "toile d'araignée", "spider chart" → radar

Provide analysis as JSON:
{{
    "language": "french|english",
    "intent_analysis": {{
        "primary_intent": "customer_analysis|sales_analysis|product_analysis|temporal_analysis|geographic_analysis|general",
        "intent_confidence": 0.9,
        "business_scenario": "customer_ranking|product_performance|sales_trends|inventory_status|customer_demographics"
    }},
    "visualization_preferences": {{
        "user_requested_chart_type": "line|bar|horizontal_bar|pie|doughnut|scatter|radar|auto",
        "chart_type_confidence": 0.8,
        "chart_keywords_detected": ["courbe", "évolution"]
    }},
    "table_analysis": {{
        "required_tables": ["table1", "table2"],
        "primary_table": "main_table"
    }},
    "join_analysis": {{
        "required_joins": [
            {{
                "from_table": "table1",
                "to_table": "table2",
                "join_condition": "table1.col = table2.col",
                "purpose": "why needed"
            }}
        ]
    }},
    "column_analysis": {{
        "select_columns": [
            {{"column": "table.column", "purpose": "grouping|aggregation", "alias": "name"}}
        ],
        "aggregation_needed": true,
        "grouping_columns": ["table.column"]
    }},
    "temporal_analysis": {{
        "needs_time_filter": true,
        "time_column": "order_date",
        "time_period": "7 days",
        "time_filter_sql": "WHERE order_date >= date('now', '-7 days')"
    }},
    "output_requirements": {{
        "needs_percentage": false,
        "suggested_limit": 10,
        "sort_order": "DESC"
    }}
}}

**CRITICAL:** If user explicitly mentions a chart type, set user_requested_chart_type to that type and confidence to 0.9+. If no chart type mentioned, set to "auto".

JSON Response:"""

        try:
            response = self.llm._call(prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            raise

    def _parse_analysis(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM JSON response safely."""
        try:
            # Clean response
            clean_response = llm_response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]

            parsed = json.loads(clean_response.strip())
            return parsed

        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {e}")
            # Fallback to basic analysis
            return self._create_fallback_analysis(llm_response)

    def _create_fallback_analysis(self, response: str) -> Dict[str, Any]:
        """Create fallback analysis if JSON parsing fails."""
        response_lower = response.lower()

        # Detect language
        language = "french" if any(word in response_lower for word in ['français', 'répartition', 'clients', 'données']) else "english"

        # Detect intent based on available tables
        if any(word in response_lower for word in ['customer', 'client']):
            primary_intent = "customer_analysis"
            tables = ["customers", "orders"]
        elif any(word in response_lower for word in ['product', 'inventory', 'stock']):
            primary_intent = "product_analysis"
            tables = ["products", "orders"]
        elif any(word in response_lower for word in ['order', 'sales', 'revenue']):
            primary_intent = "sales_analysis"
            tables = ["orders", "customers"]
        else:
            primary_intent = "general"
            tables = list(TABLE_SCHEMAS.keys())[:2]  # Use first 2 tables

        return {
            "language": language,
            "intent_analysis": {
                "primary_intent": primary_intent,
                "intent_confidence": 0.7,
                "business_scenario": primary_intent
            },
            "visualization_preferences": {
                "user_requested_chart_type": "auto",
                "chart_type_confidence": 0.5,
                "chart_keywords_detected": []
            },
            "table_analysis": {
                "required_tables": tables,
                "primary_table": tables[0] if tables else "customers"
            },
            "join_analysis": {"required_joins": []},
            "column_analysis": {"select_columns": [], "aggregation_needed": True},
            "temporal_analysis": {"needs_time_filter": False},
            "output_requirements": {"suggested_limit": 100, "sort_order": "DESC"}
        }

    def _validate_analysis(self, parsed_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance analysis results."""

        # Ensure required tables exist
        table_analysis = parsed_analysis.get('table_analysis', {})
        required_tables = table_analysis.get('required_tables', [])

        valid_tables = [table for table in required_tables if table in TABLE_SCHEMAS]
        if not valid_tables:
            valid_tables = list(TABLE_SCHEMAS.keys())[:2]  # Fallback to first 2 tables

        parsed_analysis['table_analysis']['required_tables'] = valid_tables

        # Set confidence
        intent_confidence = parsed_analysis.get('intent_analysis', {}).get('intent_confidence', 0.5)
        table_confidence = 1.0 if len(valid_tables) == len(required_tables) else 0.7

        parsed_analysis['overall_confidence'] = (intent_confidence + table_confidence) / 2

        return parsed_analysis