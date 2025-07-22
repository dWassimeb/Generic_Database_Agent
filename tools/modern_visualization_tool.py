"""
FIXED & RESTRUCTURED Modern Visualization Tool - Comprehensive Database Support
Fixed numeric detection issue and reorganized by theme and utility
Removed duplicate methods and kept the most performant versions
"""

from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from pydantic import Field
import json
import os
import logging
from datetime import datetime, date
from decimal import Decimal
from llm.custom_gpt import CustomGPT
import unicodedata
import re

logger = logging.getLogger(__name__)

class ModernVisualizationTool(BaseTool):
    """Create professional, minimalistic visualizations with intelligent date/time formatting."""

    name: str = "create_visualization"
    description: str = """
    Generate clean, professional charts and dashboards from query results.
    Creates HTML files with Chart.js visualizations with intelligent date/time formatting.
    """

    export_dir: str = Field(default="visualizations")
    llm: CustomGPT = Field(default_factory=CustomGPT)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create visualizations directory if it doesn't exist
        os.makedirs(self.export_dir, exist_ok=True)

    # ========================================
    # MAIN ENTRY POINT
    # ========================================

    def _run(self, query_result: Dict[str, Any], user_question: str = "", csv_result: Dict[str, Any] = None,
             intent_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create professional visualization from query results with user preferences."""
        try:
            # Check if we have visualizable data
            if not self._is_visualizable(query_result):
                return {
                    'success': False,
                    'message': 'Data is not suitable for visualization',
                    'reason': 'No numeric data or insufficient rows'
                }

            # Get data
            result_data = query_result.get('result', {})
            columns = result_data.get('columns', [])
            data = result_data.get('data', [])

            if self._should_log_debug():
                logger.info(f"Visualization Input - Columns: {columns}")
                logger.info(f"Visualization Input - Sample data: {data[:3] if data else 'No data'}")

            # Clean data
            cleaned_data = self._clean_data_utf8(data)

            # Extract user chart preference from intent analysis
            user_chart_preference = self._extract_user_chart_preference(intent_analysis)

            # Analyze data structure and determine best visualization type
            viz_analysis = self._analyze_data_for_visualization(columns, cleaned_data, user_question, user_chart_preference)

            if self._should_log_debug():
                logger.info(f"LLM Analysis Result: {viz_analysis}")

            # Generate the visualization
            html_file = self._create_professional_visualization(columns, cleaned_data, viz_analysis, user_question)

            # Get file stats
            file_stats = self._get_file_stats(html_file)

            return {
                'success': True,
                'html_file': html_file,
                'visualization_type': viz_analysis.get('chart_type'),
                'file_stats': file_stats,
                'message': f"Professional visualization created: {os.path.basename(html_file)}"
            }

        except Exception as e:
            logger.error(f"Visualization creation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to create visualization: {str(e)}"
            }

    # ========================================
    # UNIVERSAL NUMERIC TYPE DETECTION
    # ========================================

    def _get_numeric_types(self) -> tuple:
        """Get all possible numeric types from different databases and Python."""
        base_types = (int, float, Decimal)

        # Try to import additional numeric types that might exist
        additional_types = []

        try:
            import numpy as np
            additional_types.extend([
                np.int8, np.int16, np.int32, np.int64,
                np.uint8, np.uint16, np.uint32, np.uint64,
                np.float16, np.float32, np.float64,
                np.number  # Generic numpy number
            ])
        except ImportError:
            pass

        try:
            # ClickHouse types (if available)
            from clickhouse_driver import types as ch_types
            # ClickHouse returns various numeric types
        except ImportError:
            pass

        return base_types + tuple(additional_types)

    def _is_numeric_value(self, value: Any) -> bool:
        """Universal numeric value detection - works with ALL database types."""
        if value is None:
            return False

        # Check against all known numeric types
        numeric_types = self._get_numeric_types()
        if isinstance(value, numeric_types):
            return True

        # Additional checks for edge cases
        if hasattr(value, '__float__'):  # Duck typing - can be converted to float
            try:
                float(value)
                return True
            except (ValueError, TypeError):
                pass

        # String that represents a number
        if isinstance(value, str):
            try:
                float(value.replace(',', ''))  # Handle comma-separated numbers
                return True
            except (ValueError, TypeError):
                pass

        return False

    def _to_float(self, value: Any) -> float:
        """Universal numeric conversion - handles ALL database numeric types."""
        if value is None:
            return 0.0

        # Direct numeric types
        if isinstance(value, (int, float)):
            return float(value)

        # PostgreSQL Decimal
        if isinstance(value, Decimal):
            return float(value)

        # NumPy types
        if hasattr(value, 'item'):  # NumPy scalar
            return float(value.item())
        elif hasattr(value, '__float__'):
            return float(value)

        # String conversion
        if isinstance(value, str):
            try:
                # Handle comma-separated numbers
                cleaned = value.replace(',', '')
                return float(cleaned)
            except (ValueError, TypeError):
                return 0.0

        # Last resort
        try:
            return float(value)
        except:
            return 0.0

    # ========================================
    # DATA VALIDATION & ANALYSIS
    # ========================================

    def _is_visualizable(self, query_result: Dict[str, Any]) -> bool:
        """FIXED: Check if query results are suitable for visualization using universal numeric detection."""
        if not query_result.get('success', True):
            logger.info("Query was not successful")
            return False

        result_data = query_result.get('result', {})
        data = result_data.get('data', [])
        columns = result_data.get('columns', [])

        # Need at least 1 row and 2 columns for meaningful visualization
        if len(data) < 1 or len(columns) < 2:
            logger.info(f"Insufficient data: {len(data)} rows, {len(columns)} columns")
            return False

        # Debug the data types
        self._debug_data_types(data)

        # FIXED: Use universal numeric detection instead of basic isinstance check
        has_numeric = False
        numeric_columns = []

        for i, col in enumerate(columns):
            if self._column_is_numeric_by_index(i, data):
                has_numeric = True
                numeric_columns.append(col)

        logger.info(f"Data validation: {len(data)} rows, {len(columns)} columns")
        logger.info(f"Numeric columns found: {numeric_columns}")
        logger.info(f"Has numeric data: {has_numeric}")

        return has_numeric

    def _column_is_numeric_by_index(self, col_index: int, data: List[List]) -> bool:
        """UNIVERSAL: Check if a column contains primarily numeric data by index."""
        sample_values = [row[col_index] for row in data[:5] if col_index < len(row) and row[col_index] is not None]

        if not sample_values:
            return False

        # Use universal numeric detection with threshold
        numeric_count = sum(1 for val in sample_values if self._is_numeric_value(val))
        is_numeric = numeric_count >= len(sample_values) * 0.8  # 80% threshold

        if self._should_log_debug():
            logger.info(f"Column {col_index}: {numeric_count}/{len(sample_values)} numeric values = {is_numeric}")

        return is_numeric

    def _column_is_numeric(self, column_name: str, columns: List[str], data: List[List]) -> bool:
        """UNIVERSAL: Check if a column contains primarily numeric data."""
        try:
            col_index = columns.index(column_name)
            return self._column_is_numeric_by_index(col_index, data)
        except ValueError:
            logger.warning(f"Column '{column_name}' not found in {columns}")
            return False

    def _analyze_column_types(self, columns: List[str], data: List[List]) -> Dict[str, str]:
        """UNIVERSAL: Analyze what type of data each column contains."""
        column_types = {}

        for i, col in enumerate(columns):
            sample_values = [row[i] for row in data[:20] if i < len(row) and row[i] is not None]

            if not sample_values:
                column_types[col] = 'empty'
            elif all(self._is_numeric_value(val) for val in sample_values):
                column_types[col] = 'numeric'
            elif all(isinstance(val, str) for val in sample_values):
                column_types[col] = 'text'
            else:
                column_types[col] = 'mixed'

        if self._should_log_debug():
            logger.info(f"Column types analysis: {column_types}")

        return column_types

    def _perform_comprehensive_data_analysis(self, columns: List[str], data: List[List]) -> Dict[str, Any]:
        """UNIVERSAL: Perform comprehensive analysis of data patterns."""
        analysis = {
            'column_types': {},
            'data_patterns': {},
            'relationships': {},
            'distributions': {}
        }

        for i, col in enumerate(columns):
            sample_values = [row[i] for row in data[:20] if i < len(row) and row[i] is not None]

            if not sample_values:
                analysis['column_types'][col] = 'empty'
                continue

            # FIXED: Universal numeric detection
            if all(self._is_numeric_value(val) for val in sample_values):
                analysis['column_types'][col] = 'numeric'
                # Analyze numeric patterns
                values = [self._to_float(val) for val in sample_values]
                analysis['data_patterns'][col] = {
                    'min': min(values),
                    'max': max(values),
                    'range': max(values) - min(values),
                    'avg': sum(values) / len(values),
                    'has_large_range': (max(values) - min(values)) > 1000
                }
            elif all(isinstance(val, str) for val in sample_values):
                analysis['column_types'][col] = 'text'
                # Analyze categorical patterns
                unique_values = list(set(sample_values))
                analysis['distributions'][col] = {
                    'unique_count': len(unique_values),
                    'total_count': len(sample_values),
                    'uniqueness_ratio': len(unique_values) / len(sample_values),
                    'sample_values': unique_values[:5]
                }
                # Check if it might be dates
                if any(self._might_be_date(val) for val in sample_values[:3]):
                    analysis['column_types'][col] = 'datetime'
            else:
                analysis['column_types'][col] = 'mixed'

        # Detect relationships between numeric columns
        numeric_columns = [col for col, type_ in analysis['column_types'].items() if type_ == 'numeric']
        if len(numeric_columns) >= 2:
            analysis['relationships']['has_multiple_numeric'] = True
            analysis['relationships']['numeric_columns'] = numeric_columns

        return analysis

    def _find_first_numeric_column(self, columns: List[str], data: List[List]) -> Optional[str]:
        """UNIVERSAL: Find the first column that contains numeric data."""
        for i, col in enumerate(columns):
            if self._column_is_numeric_by_index(i, data):
                return col
        return None

    # ========================================
    # TIME SERIES DETECTION
    # ========================================

    def _detect_time_series_columns(self, columns: List[str], data: List[List]) -> Dict[str, Any]:
        """ENHANCED: Better detection of time series data with support for datetime objects."""

        time_info = {
            'is_time_series': False,
            'date_column': None,
            'datetime_column': None,
            'value_column': None,
            'time_format': 'unknown',
            'sample_dates': []
        }

        # Check each column for time-related data
        for i, col in enumerate(columns):
            col_lower = col.lower()
            sample_values = [row[i] for row in data[:5] if i < len(row) and row[i] is not None]

            if not sample_values:
                continue

            # Check if column contains datetime objects or date objects
            if any(isinstance(val, (datetime, date)) for val in sample_values):
                if any(isinstance(val, datetime) for val in sample_values):
                    time_info['datetime_column'] = {'name': col, 'index': i}
                    time_info['time_format'] = 'datetime_object'
                elif any(isinstance(val, date) for val in sample_values):
                    time_info['date_column'] = {'name': col, 'index': i}
                    time_info['time_format'] = 'date_object'

                time_info['sample_dates'] = sample_values[:3]

            # Check column names for time-related patterns
            elif any(keyword in col_lower for keyword in ['date', 'time', 'day', 'month', 'year']):
                # Check if values look like dates
                if self._values_look_like_dates(sample_values):
                    time_info['date_column'] = {'name': col, 'index': i}
                    time_info['time_format'] = 'string_date'
                    time_info['sample_dates'] = sample_values[:3]

            # Check for value columns
            elif any(val_word in col_lower for val_word in ['count', 'amount', 'volume', 'total', 'sum', 'ticket']):
                if self._column_is_numeric_by_index(i, data):
                    time_info['value_column'] = {'name': col, 'index': i}

        # Determine if this is time series
        has_time_component = (time_info['date_column'] or time_info['datetime_column'])
        has_value_component = time_info['value_column'] or any(
            self._column_is_numeric_by_index(i, data) for i in range(len(columns))
        )

        time_info['is_time_series'] = has_time_component and has_value_component

        if self._should_log_debug():
            logger.info(f"Enhanced time series detection: {time_info}")

        return time_info

    def _values_look_like_dates(self, values: List[Any]) -> bool:
        """Check if string values look like dates."""
        if not values:
            return False

        # Check if most values match common date patterns
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
        ]

        date_like_count = 0
        for value in values:
            if isinstance(value, str):
                for pattern in date_patterns:
                    if re.search(pattern, value):
                        date_like_count += 1
                        break

        return date_like_count >= len(values) * 0.5  # At least 50% look like dates

    def _might_be_date(self, value: str) -> bool:
        """Check if a string value might be a date."""
        if not isinstance(value, str):
            return False

        # Simple date pattern detection
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
            r'\d{4}-\d{2}',        # YYYY-MM (month format)
        ]

        return any(re.search(pattern, value) for pattern in date_patterns)

    # ========================================
    # DATA CLEANING & PREPARATION
    # ========================================

    def _clean_data_utf8(self, data: List[List]) -> List[List]:
        """Clean data to handle UTF-8 encoding issues."""
        cleaned_data = []

        for row in data:
            cleaned_row = []
            for value in row:
                if isinstance(value, str):
                    # Clean the string to remove problematic characters
                    cleaned_value = self._clean_string_utf8(value)
                    cleaned_row.append(cleaned_value)
                else:
                    cleaned_row.append(value)
            cleaned_data.append(cleaned_row)

        return cleaned_data

    def _clean_string_utf8(self, text: str) -> str:
        """Clean a string to ensure it's UTF-8 compatible."""
        if not text:
            return text

        try:
            # Normalize the string
            normalized = unicodedata.normalize('NFKD', text)
            # Remove non-ASCII characters that might cause issues
            cleaned = re.sub(r'[^\x00-\x7F]+', '', normalized)
            # If the cleaned string is empty, try a different approach
            if not cleaned.strip():
                # Keep only alphanumeric and common punctuation
                cleaned = re.sub(r'[^\w\s\-\.\/\(\)&]+', '', text)
            return cleaned.strip()
        except:
            # Last resort: convert to ASCII
            return text.encode('ascii', 'ignore').decode('ascii')

    # ========================================
    # CHART ANALYSIS & CONFIGURATION
    # ========================================

    def _analyze_data_for_visualization(self, columns: List[str], data: List[List], user_question: str,
                                       user_chart_preference: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced analysis with user chart preference support and intelligent time detection."""

        # Detect time series with enhanced detection
        time_info = self._detect_time_series_columns(columns, data)

        # Prepare comprehensive data analysis
        sample_data = []
        for i, row in enumerate(data[:5]):
            row_dict = {}
            for j, col in enumerate(columns):
                if j < len(row):
                    value = row[j]
                    if isinstance(value, str):
                        value = self._clean_string_utf8(value)
                    row_dict[col] = value
            sample_data.append(row_dict)

        # Enhanced data type analysis
        data_analysis = self._perform_comprehensive_data_analysis(columns, data)
        question_context = self._analyze_question_context(user_question)

        data_structure = {
            'columns': columns,
            'sample_data': sample_data,
            'total_rows': len(data),
            'data_analysis': data_analysis,
            'question_context': question_context,
            'time_series_info': time_info,
            'user_chart_preference': user_chart_preference
        }

        # Enhanced prompt with user preference support
        user_preference_instruction = ""
        if user_chart_preference:
            user_preference_instruction = f"""
    **🎯 USER EXPLICITLY REQUESTED: {user_chart_preference.upper()} CHART**
    - PRIORITY: Honor the user's explicit request unless technically impossible
    - Only override if the requested chart type is completely incompatible with the data
    - Provide reasoning if you need to suggest an alternative
    """

        prompt = f"""Analyze this query result and determine the BEST visualization approach.

    User Question: "{user_question}"
    Data Structure: {json.dumps(data_structure, indent=2, default=str, ensure_ascii=True)}

    {user_preference_instruction}

    **TIME SERIES DETECTION:**
    Is Time Series: {time_info['is_time_series']}
    Time Columns: {[col['name'] for col in [time_info.get('date_column'), time_info.get('datetime_column')] if col]}

    **AVAILABLE CHART TYPES:**
    - **line** - Time series, trends, evolution over time
    - **area** - Time series with filled area
    - **bar** - Categorical comparisons (vertical bars)
    - **horizontal_bar** - Rankings/top N lists (horizontal bars)
    - **pie** - Distributions (≤8 categories)
    - **doughnut** - Modern pie charts with center hole
    - **scatter** - Correlations between variables
    - **radar** - Multi-dimensional comparisons

    **SELECTION PRIORITY:**
    1. **User's explicit request** (if technically feasible)
    2. **Data compatibility** (time series → line, rankings → horizontal_bar)
    3. **Question context** (evolution → line, top N → horizontal_bar)

    Respond ONLY with valid JSON:
    {{
        "chart_type": "line|area|bar|horizontal_bar|pie|doughnut|scatter|radar",
        "title": "Clean descriptive title",
        "label_column": "column_for_x_axis_or_categories",
        "value_column": "column_for_y_axis_or_values",
        "color_scheme": "professional_blue",
        "show_legend": false,
        "user_preference_honored": true,
        "reasoning": "Why this chart type was chosen, mentioning user preference if applicable"
    }}

    **REMEMBER:** Honor user's chart preference when possible!

    JSON Response:"""

        try:
            response = self.llm._call(prompt)
            clean_response = response.strip()

            # Clean JSON response
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]

            json_end = clean_response.rfind('}')
            if json_end != -1:
                clean_response = clean_response[:json_end + 1]

            parsed = json.loads(clean_response.strip())

            # Override: Force user preference if specified and reasonable
            if user_chart_preference and not parsed.get('user_preference_honored'):
                # Check if user preference is reasonable for the data
                if self._is_chart_type_compatible(user_chart_preference, time_info, len(data)):
                    parsed['chart_type'] = user_chart_preference
                    parsed['user_preference_honored'] = True
                    parsed['reasoning'] = f"Using user-requested {user_chart_preference} chart type"

            # Enhanced validation
            validated_analysis = self._validate_and_enhance_chart_analysis(parsed, columns, data, user_question)
            return validated_analysis

        except Exception as e:
            logger.warning(f"LLM visualization analysis failed: {e}")
            return self._create_intelligent_fallback_analysis(columns, data, user_question, time_info)

    def _analyze_question_context(self, user_question: str) -> Dict[str, Any]:
        """Analyze question for visualization hints."""

        question_lower = user_question.lower()

        context = {
            'asks_for_distribution': any(word in question_lower for word in ['distribution', 'breakdown', 'percentage', 'proportion', 'share']),
            'asks_for_ranking': any(word in question_lower for word in ['top', 'bottom', 'ranking', 'highest', 'lowest', 'best', 'worst']),
            'asks_for_trend': any(word in question_lower for word in ['trend', 'over time', 'timeline', 'progression', 'evolution', 'évolution', 'journalière']),
            'asks_for_comparison': any(word in question_lower for word in ['compare', 'comparison', 'versus', 'vs', 'between']),
            'asks_for_correlation': any(word in question_lower for word in ['correlation', 'relationship', 'related', 'depends on']),
            'mentions_time': any(word in question_lower for word in ['time', 'date', 'month', 'year', 'day', 'hour', 'period', 'journalière', 'daily']),
            'has_specific_count': any(word in question_lower for word in ['top 5', 'top 10', 'first 20', 'last 15'])
        }

        return context

    def _extract_user_chart_preference(self, intent_analysis: Dict[str, Any]) -> Optional[str]:
        """Extract user's chart type preference from intent analysis."""
        if not intent_analysis:
            return None

        viz_prefs = intent_analysis.get('visualization_preferences', {})
        user_requested = viz_prefs.get('user_requested_chart_type')
        confidence = viz_prefs.get('chart_type_confidence', 0.0)

        # Only use user preference if confidence is high enough
        if user_requested and user_requested != 'auto' and confidence >= 0.7:
            if self._should_log_debug():
                logger.info(f"User requested chart type: {user_requested} (confidence: {confidence})")
            return user_requested

        return None

    def _is_chart_type_compatible(self, chart_type: str, time_info: Dict[str, Any], data_count: int) -> bool:
        """Check if user-requested chart type is compatible with the data."""

        # Time series data should use line/area charts
        if time_info.get('is_time_series') and chart_type not in ['line', 'area']:
            return False

        # Pie charts only work with small datasets
        if chart_type in ['pie', 'doughnut'] and data_count > 8:
            return False

        # Otherwise, most chart types are flexible
        return True

    def _validate_and_enhance_chart_analysis(self, parsed: Dict[str, Any], columns: List[str], data: List[List], user_question: str) -> Dict[str, Any]:
        """Validate and enhance the LLM's chart analysis."""

        chart_type = parsed.get('chart_type', 'bar')

        # Validate chart type
        valid_types = ['bar', 'horizontal_bar', 'line', 'area', 'pie', 'doughnut', 'scatter', 'bubble', 'radar', 'polar']
        if chart_type not in valid_types:
            chart_type = 'bar'
            parsed['chart_type'] = chart_type

        # Validate column assignments
        label_col = parsed.get('label_column', '')
        value_col = parsed.get('value_column', '')

        # Ensure columns exist
        if label_col not in columns:
            # Find first text column or use first column
            text_cols = [col for col in columns if not self._column_is_numeric(col, columns, data)]
            parsed['label_column'] = text_cols[0] if text_cols else columns[0]

        if value_col not in columns:
            # Find first numeric column or use last column
            numeric_cols = [col for col in columns if self._column_is_numeric(col, columns, data)]
            parsed['value_column'] = numeric_cols[0] if numeric_cols else columns[-1]

        # Add intelligent defaults based on chart type
        if chart_type in ['pie', 'doughnut']:
            parsed['show_legend'] = True
            parsed['chart_specific_options'] = parsed.get('chart_specific_options', {})
            parsed['chart_specific_options']['show_data_labels'] = True

        elif chart_type in ['line', 'area']:
            parsed['chart_specific_options'] = parsed.get('chart_specific_options', {})
            parsed['chart_specific_options']['enable_zoom'] = True

        elif chart_type in ['scatter', 'bubble']:
            parsed['chart_specific_options'] = parsed.get('chart_specific_options', {})
            parsed['chart_specific_options']['show_correlation'] = True

        # Ensure we have a reasoning
        if not parsed.get('reasoning'):
            parsed['reasoning'] = f"Selected {chart_type} chart based on data structure and question context"

        return parsed

    def _create_intelligent_fallback_analysis(self, columns: List[str], data: List[List], user_question: str, time_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create intelligent fallback when LLM fails."""

        # If it's time series data, force line chart
        if time_info and time_info['is_time_series']:
            chart_type = 'line'
            reasoning = "Time series data detected - using line chart"

            # Determine columns
            if time_info.get('datetime_column'):
                label_column = time_info['datetime_column']['name']
            elif time_info.get('date_column'):
                label_column = time_info['date_column']['name']
            else:
                label_column = columns[0]

            if time_info.get('value_column'):
                value_column = time_info['value_column']['name']
            else:
                # Find first numeric column that's not a time column
                value_column = None
                time_columns = [
                    time_info.get('datetime_column', {}).get('name'),
                    time_info.get('date_column', {}).get('name')
                ]

                for col in columns:
                    if col not in time_columns and self._column_is_numeric(col, columns, data):
                        value_column = col
                        break

                if not value_column:
                    value_column = columns[-1] if columns else 'Value'

        else:
            # Use standard fallback logic
            column_types = self._analyze_column_types(columns, data)
            question_context = self._analyze_question_context(user_question)

            text_columns = [col for col, type_ in column_types.items() if type_ == 'text']
            numeric_columns = [col for col, type_ in column_types.items() if type_ == 'numeric']

            # Chart type selection
            if question_context['asks_for_ranking'] or 'top' in user_question.lower():
                chart_type = 'horizontal_bar'
                reasoning = "Horizontal bar chart for ranking analysis"
            elif question_context['asks_for_distribution'] and len(text_columns) == 1 and len(data) <= 8:
                chart_type = 'pie'
                reasoning = "Pie chart for small distribution"
            elif len(data) > 15:
                chart_type = 'horizontal_bar'
                reasoning = "Horizontal bar chart for many categories"
            else:
                chart_type = 'bar'
                reasoning = "Default bar chart"

            label_column = text_columns[0] if text_columns else columns[0]
            value_column = numeric_columns[0] if numeric_columns else columns[-1]

        return {
            "chart_type": chart_type,
            "title": "Data Analysis",
            "label_column": label_column,
            "value_column": value_column,
            "color_scheme": "professional_blue",
            "show_legend": chart_type in ['pie', 'doughnut', 'line'],
            "reasoning": f"Intelligent fallback: {reasoning}"
        }

    # ========================================
    # DATA PREPARATION FOR CHARTS
    # ========================================

    def _prepare_chart_data(self, columns: List[str], data: List[List], viz_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """FIXED: Prepare data with proper time series handling and intelligent date formatting."""

        chart_type = viz_analysis.get('chart_type', 'bar')

        # Enhanced logic to detect time series data
        time_info = self._detect_time_series_columns(columns, data)

        if time_info['is_time_series']:
            # Handle time series data with FIXED date formatting
            return self._prepare_time_series_data(columns, data, viz_analysis, time_info)
        else:
            # Use the corrected column names from the analysis
            label_col = viz_analysis.get('label_column', columns[0] if columns else 'Category')
            value_col = viz_analysis.get('value_column', columns[1] if len(columns) > 1 else 'Value')

            return self._prepare_standard_data(columns, data, viz_analysis, label_col, value_col)

    def _prepare_standard_data(self, columns: List[str], data: List[List], viz_analysis: Dict[str, Any],
                               label_col: str, value_col: str) -> Dict[str, Any]:
        """UNIVERSAL: Prepare standard chart data with universal numeric support."""

        chart_type = viz_analysis.get('chart_type', 'bar')

        try:
            label_idx = columns.index(label_col)
            value_idx = columns.index(value_col)
        except ValueError as e:
            logger.error(f"Column not found: {e}")
            return {'labels': [], 'values': [], 'chart_type': chart_type, 'is_time_series': False}

        labels = []
        values = []

        if self._should_log_debug():
            logger.info(f"Standard data preparation:")
            logger.info(f"  Chart type: {chart_type}")
            logger.info(f"  Columns available: {columns}")
            logger.info(f"  Label column (categories): {label_col}")
            logger.info(f"  Value column (numbers): {value_col}")
            logger.info(f"  Final mapping: Label='{label_col}'[{label_idx}], Value='{value_col}'[{value_idx}]")

        for row_idx, row in enumerate(data):
            if label_idx < len(row) and value_idx < len(row):
                raw_label = row[label_idx]
                raw_value = row[value_idx]

                # Handle label
                if raw_label is None:
                    label = f"Item {row_idx + 1}"
                else:
                    label = str(raw_label)

                # Handle value with UNIVERSAL numeric conversion
                value = self._to_float(raw_value)

                labels.append(label)
                values.append(value)

                # Debug first few mappings
                if self._should_log_debug() and row_idx < 3:
                    logger.info(
                        f"  Row {row_idx}: '{raw_label}' -> '{label}', {raw_value} ({type(raw_value).__name__}) -> {value}")

        # Limit data points for better visualization
        if len(labels) > 50:
            labels = labels[:50]
            values = values[:50]

        if self._should_log_debug():
            logger.info(f"  Final data - Labels: {labels[:3]}, Values: {values[:3]}")

        return {
            'labels': labels,
            'values': values,
            'x_axis': label_col,
            'y_axis': value_col,
            'chart_type': chart_type,
            'is_time_series': False
        }

    def _prepare_time_series_data(self, columns: List[str], data: List[List], viz_analysis: Dict[str, Any], time_info: Dict[str, Any]) -> Dict[str, Any]:
        """FIXED: Prepare time series data with intelligent date formatting."""

        chart_type = viz_analysis.get('chart_type', 'line')

        # Build time series labels and values
        labels = []
        values = []

        # Determine which column contains the time data
        time_column_info = time_info.get('date_column') or time_info.get('datetime_column')
        if not time_column_info:
            # Fallback to standard data preparation
            return self._prepare_standard_data(columns, data, viz_analysis, columns[0], columns[1] if len(columns) > 1 else columns[0])

        time_col_index = time_column_info['index']
        time_format = time_info.get('time_format', 'unknown')

        # Determine value column
        value_col_info = time_info.get('value_column')
        if value_col_info:
            value_col_index = value_col_info['index']
            value_col_name = value_col_info['name']
        else:
            # Find first numeric column that's not the time column
            value_col_index = None
            value_col_name = 'Value'
            for i, col in enumerate(columns):
                if i != time_col_index and self._column_is_numeric_by_index(i, data):
                    value_col_index = i
                    value_col_name = col
                    break

            if value_col_index is None:
                value_col_index = 1 if len(columns) > 1 and time_col_index != 1 else 0
                value_col_name = columns[value_col_index] if value_col_index < len(columns) else 'Value'

        # Sort data by time column
        try:
            sorted_data = sorted(data, key=lambda row: row[time_col_index] if time_col_index < len(row) else 0)
        except:
            sorted_data = data

        # Process each row and format dates intelligently
        for row in sorted_data:
            if time_col_index >= len(row) or value_col_index >= len(row):
                continue

            # Get and format the time value
            time_value = row[time_col_index]
            formatted_label = self._format_time_value_intelligently(time_value, time_format)
            labels.append(formatted_label)

            # Get the numeric value
            raw_value = row[value_col_index]
            value = self._to_float(raw_value)
            values.append(value)

        if self._should_log_debug():
            logger.info(f"FIXED time series data - Labels: {labels[:3]}, Values: {values[:3]}")

        return {
            'labels': labels,
            'values': values,
            'x_axis': time_column_info['name'],
            'y_axis': value_col_name,
            'chart_type': chart_type,
            'is_time_series': True
        }

    # ========================================
    # TIME VALUE FORMATTING
    # ========================================

    def _format_time_value_intelligently(self, time_value: Any, time_format: str) -> str:
        """FIXED: Intelligently format time values for chart labels."""

        if time_value is None:
            return "Unknown"

        try:
            # Handle datetime objects
            if isinstance(time_value, datetime):
                return self._format_datetime_for_chart(time_value)

            # Handle date objects
            elif isinstance(time_value, date):
                return self._format_date_for_chart(time_value)

            # Handle string dates
            elif isinstance(time_value, str):
                return self._format_string_date_for_chart(time_value)

            # Handle numeric values that might represent time
            elif isinstance(time_value, (int, float)):
                return self._format_numeric_time_for_chart(time_value)

            else:
                return str(time_value)

        except Exception as e:
            if self._should_log_debug():
                logger.warning(f"Error formatting time value {time_value}: {e}")
            return str(time_value)

    def _format_datetime_for_chart(self, dt: datetime) -> str:
        """Format datetime objects for chart display."""
        # For datetime, show date + time if time is significant
        if dt.hour != 0 or dt.minute != 0 or dt.second != 0:
            return dt.strftime("%Y-%m-%d %H:%M")
        else:
            return dt.strftime("%Y-%m-%d")

    def _format_date_for_chart(self, d: date) -> str:
        """Format date objects for chart display."""
        return d.strftime("%Y-%m-%d")

    def _format_string_date_for_chart(self, date_str: str) -> str:
        """Format string dates for chart display."""
        # Try to parse common date formats and reformat them
        common_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M"
        ]

        for fmt in common_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

        # If parsing fails, return as is but cleaned
        return self._clean_string_utf8(date_str)

    def _format_numeric_time_for_chart(self, num_value: float) -> str:
        """Format numeric time values (like timestamps or years)."""
        # If it looks like a year (1900-2100), format as year
        if 1900 <= num_value <= 2100:
            return str(int(num_value))

        # If it looks like a timestamp, try to convert
        elif num_value > 1000000000:  # Unix timestamp
            try:
                dt = datetime.fromtimestamp(num_value)
                return dt.strftime("%Y-%m-%d")
            except:
                return str(int(num_value))

        else:
            return str(int(num_value))

    # ========================================
    # HTML VISUALIZATION GENERATION
    # ========================================

    def _create_professional_visualization(self, columns: List[str], data: List[List], viz_analysis: Dict[str, Any], user_question: str) -> str:
        """Create the professional HTML visualization file with safe UTF-8 handling."""

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chart_{timestamp}.html"
        filepath = os.path.join(self.export_dir, filename)

        # Prepare chart data using the fixed method
        chart_data = self._prepare_chart_data(columns, data, viz_analysis)

        if self._should_log_debug():
            logger.info(f"Chart data prepared: {chart_data}")

        # Generate HTML content
        html_content = self._generate_streamlit_optimized_html_template(chart_data, viz_analysis, user_question)

        # Write to file with proper encoding
        try:
            with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
                f.write(html_content)
        except UnicodeEncodeError:
            # Fallback to ASCII if UTF-8 fails
            with open(filepath, 'w', encoding='ascii', errors='replace') as f:
                f.write(html_content)

        logger.info(f"Professional visualization created: {filepath}")
        return filepath

    def _generate_streamlit_optimized_html_template(self, chart_data: Dict[str, Any], viz_analysis: Dict[str, Any], user_question: str) -> str:
        """Generate HTML template optimized for Streamlit container."""

        chart_type = viz_analysis.get('chart_type', 'bar')
        title = self._clean_string_utf8(viz_analysis.get('title', 'Data Analysis'))
        clean_user_question = self._clean_string_utf8(user_question)

        # Professional color schemes
        colors = ['#4299e1', '#63b3ed', '#90cdf4', '#bee3f8', '#ebf8ff']

        # Generate Chart.js configuration
        chart_config = self._generate_professional_chart_config(chart_data, viz_analysis, colors)

        # Clean data for JSON serialization
        clean_labels = [self._clean_string_utf8(str(label)) for label in chart_data['labels']]
        clean_values = chart_data['values']

        # Streamlit-optimized template
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #ffffff;
            color: #2d3748;
            line-height: 1.5;
            padding: 0;
        }}
        
        .container {{
            width: 100%;
            height: 100vh;
            background: #ffffff;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        
        .header {{
            background: #ffffff;
            border-bottom: 1px solid #e2e8f0;
            padding: 12px 16px;
            flex-shrink: 0;
        }}
        
        .header h1 {{
            font-size: 18px;
            font-weight: 600;
            color: #1a1d29;
            margin-bottom: 4px;
        }}
        
        .header p {{
            font-size: 12px;
            color: #718096;
            font-weight: 400;
            margin: 0;
        }}
        
        .chart-container {{
            flex: 1;
            padding: 16px;
            background: #ffffff;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .chart-wrapper {{
            position: relative;
            width: 100%;
            height: 100%;
            min-height: 300px;
        }}
        
        .stats-panel {{
            background: #f8fafc;
            border-top: 1px solid #e2e8f0;
            padding: 12px 16px;
            flex-shrink: 0;
            max-height: 120px;
            overflow-y: auto;
        }}
        
        .stats-title {{
            font-size: 14px;
            font-weight: 500;
            color: #2d3748;
            margin-bottom: 8px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 8px;
        }}
        
        .stat-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 8px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 16px;
            font-weight: 600;
            color: #1a1d29;
            margin-bottom: 2px;
        }}
        
        .stat-label {{
            font-size: 10px;
            color: #718096;
            font-weight: 400;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .footer {{
            text-align: center;
            padding: 8px 16px;
            background: #f8fafc;
            border-top: 1px solid #e2e8f0;
            font-size: 10px;
            color: #a0aec0;
            flex-shrink: 0;
        }}
        
        @media (max-height: 500px) {{
            .header {{
                padding: 8px 12px;
            }}
            
            .header h1 {{
                font-size: 16px;
            }}
            
            .header p {{
                font-size: 11px;
            }}
            
            .chart-container {{
                padding: 12px;
            }}
            
            .stats-panel {{
                display: none;
            }}
            
            .footer {{
                display: none;
            }}
        }}
        
        @media (max-width: 600px) {{
            .stats-grid {{
                grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            }}
            
            .chart-container {{
                padding: 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>{clean_user_question}</p>
        </div>
        
        <div class="chart-container">
            <div class="chart-wrapper">
                <canvas id="mainChart"></canvas>
            </div>
        </div>
        
        <div class="stats-panel">
            <div class="stats-title">Analysis Summary</div>
            <div class="stats-grid" id="statsContainer">
                <!-- Stats will be populated by JavaScript -->
            </div>
        </div>
        
        <div class="footer">
            Powered by Castor • {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
        </div>
    </div>

    <script>
        // Chart configuration
        const chartConfig = {chart_config};
        
        // Create the chart with responsive sizing
        const ctx = document.getElementById('mainChart').getContext('2d');
        const mainChart = new Chart(ctx, chartConfig);
        
        // Generate statistics
        const data = {json.dumps(clean_values, ensure_ascii=True)};
        const labels = {json.dumps(clean_labels, ensure_ascii=True)};
        
        function formatNumber(num) {{
            if (Math.abs(num) >= 1000000) {{
                return (num / 1000000).toFixed(2) + 'M';
            }} else if (Math.abs(num) >= 1000) {{
                return (num / 1000).toFixed(2) + 'K';
            }} else {{
                return num.toFixed(2);
            }}
        }}
        
        function generateStats() {{
            const total = data.reduce((sum, val) => sum + val, 0);
            const average = total / data.length;
            const max = Math.max(...data);
            const min = Math.min(...data);
            
            const stats = [
                {{ label: 'Total Records', value: data.length.toString() }},
                {{ label: 'Sum', value: formatNumber(total) }},
                {{ label: 'Average', value: formatNumber(average) }},
                {{ label: 'Maximum', value: formatNumber(max) }},
                {{ label: 'Minimum', value: formatNumber(min) }}
            ];
            
            const container = document.getElementById('statsContainer');
            container.innerHTML = stats.map(stat => `
                <div class="stat-card">
                    <div class="stat-value">${{stat.value}}</div>
                    <div class="stat-label">${{stat.label}}</div>
                </div>
            `).join('');
        }}
        
        // Initialize stats
        generateStats();
        
        // Enhanced responsive behavior for Streamlit
        function handleResize() {{
            if (mainChart) {{
                mainChart.resize();
            }}
        }}
        
        window.addEventListener('resize', handleResize);
        
        // Ensure chart fits properly in Streamlit container
        document.addEventListener('DOMContentLoaded', function() {{
            setTimeout(() => {{
                if (mainChart) {{
                    mainChart.resize();
                }}
            }}, 100);
        }});
    </script>
</body>
</html>"""

        return html_template

    # ========================================
    # CHART.JS CONFIGURATION GENERATION
    # ========================================

    def _generate_professional_chart_config(self, chart_data: Dict[str, Any], viz_analysis: Dict[str, Any], colors: List[str]) -> str:
        """Generate Chart.js configuration supporting ALL chart types."""

        chart_type = viz_analysis.get('chart_type', 'bar')
        chart_options = viz_analysis.get('chart_specific_options', {})

        # Extended color schemes
        color_schemes = {
            'professional_blue': ['#4299e1', '#63b3ed', '#90cdf4', '#bee3f8', '#ebf8ff'],
            'professional_green': ['#48bb78', '#68d391', '#9ae6b4', '#c6f6d5', '#f0fff4'],
            'professional_purple': ['#9f7aea', '#b794f6', '#d6bcfa', '#e9d8fd', '#faf5ff'],
            'warm': ['#f56565', '#fc8181', '#feb2b2', '#fed7d7', '#fff5f5'],
            'cool': ['#4fd1c7', '#81e6d9', '#b2f5ea', '#c6f7f4', '#f0fdfa']
        }

        selected_colors = color_schemes.get(viz_analysis.get('color_scheme', 'professional_blue'), colors)

        # Base configuration
        config = {
            'type': self._get_chartjs_type(chart_type),
            'data': self._build_chart_data_config(chart_data, viz_analysis, selected_colors),
            'options': self._build_chart_options_config(chart_type, chart_data, viz_analysis, chart_options)
        }

        # Convert to JSON and inject JavaScript functions
        config_json = json.dumps(config, indent=2, ensure_ascii=True)

        # Inject callback functions for different chart types
        config_json = self._inject_callback_functions(config_json, chart_type)

        return config_json

    def _get_chartjs_type(self, chart_type: str) -> str:
        """Map our chart types to Chart.js types."""
        type_mapping = {
            'bar': 'bar',
            'horizontal_bar': 'bar',
            'line': 'line',
            'area': 'line',
            'pie': 'pie',
            'doughnut': 'doughnut',
            'scatter': 'scatter',
            'bubble': 'bubble',
            'radar': 'radar',
            'polar': 'polarArea'
        }
        return type_mapping.get(chart_type, 'bar')

    def _build_chart_data_config(self, chart_data: Dict[str, Any], viz_analysis: Dict[str, Any], colors: List[str]) -> Dict[str, Any]:
        """Build chart data configuration."""
        chart_type = viz_analysis.get('chart_type', 'bar')
        clean_labels = [self._clean_string_utf8(str(label)) for label in chart_data['labels']]

        if chart_type in ['pie', 'doughnut', 'polar']:
            # For pie charts, use multiple colors
            return {
                'labels': clean_labels,
                'datasets': [{
                    'label': chart_data.get('y_axis', 'Value'),
                    'data': chart_data['values'],
                    'backgroundColor': colors[:len(clean_labels)] if len(colors) >= len(clean_labels) else colors * (len(clean_labels) // len(colors) + 1),
                    'borderColor': '#ffffff',
                    'borderWidth': 2,
                    'hoverBorderWidth': 3
                }]
            }
        else:
            # For line, bar, area charts
            dataset_config = {
                'label': chart_data.get('y_axis', 'Value'),
                'data': chart_data['values'],
                'backgroundColor': colors[0],
                'borderColor': colors[0],
                'borderWidth': 2,
                'hoverBackgroundColor': colors[1] if len(colors) > 1 else colors[0],
                'hoverBorderColor': colors[0],
                'hoverBorderWidth': 3
            }

            # Chart-specific properties
            if chart_type == 'line':
                dataset_config.update({
                    'fill': False,
                    'tension': 0.3,
                    'pointRadius': 5,
                    'pointHoverRadius': 8,
                    'pointBackgroundColor': colors[0],
                    'pointBorderColor': '#ffffff',
                    'pointBorderWidth': 2
                })
            elif chart_type == 'area':
                dataset_config.update({
                    'fill': True,
                    'tension': 0.3,
                    'pointRadius': 4,
                    'pointHoverRadius': 6,
                    'backgroundColor': colors[0] + '40'  # Add transparency for area
                })
            elif chart_type in ['bar', 'horizontal_bar']:
                dataset_config.update({
                    'borderRadius': 4,
                    'borderSkipped': False
                })

            return {
                'labels': clean_labels,
                'datasets': [dataset_config]
            }

    def _build_chart_options_config(self, chart_type: str, chart_data: Dict[str, Any], viz_analysis: Dict[str, Any], chart_options: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive chart options configuration."""

        base_options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {
                    'display': viz_analysis.get('show_legend', False),
                    'position': 'top',
                    'labels': {
                        'usePointStyle': True,
                        'padding': 20,
                        'font': {
                            'size': 12,
                            'family': 'Inter',
                            'weight': '400'
                        },
                        'color': '#718096'
                    }
                },
                'tooltip': self._build_tooltip_config(chart_type)
            },
            'animation': {
                'duration': 800,
                'easing': 'easeOutQuart'
            }
        }

        # Chart-type specific options
        if chart_type in ['pie', 'doughnut']:
            base_options['plugins']['legend']['display'] = True
            base_options['plugins']['legend']['position'] = 'right'

            if chart_options.get('show_data_labels', False):
                base_options['plugins']['datalabels'] = {
                    'display': True,
                    'color': '#ffffff',
                    'font': {'weight': 'bold'}
                }

        elif chart_type in ['bar', 'horizontal_bar']:
            base_options['interaction'] = {
                'intersect': True,
                'mode': 'nearest'
            }
            base_options['scales'] = self._build_scales_config(chart_type, chart_data)

            if chart_type == 'horizontal_bar':
                base_options['indexAxis'] = 'y'

        elif chart_type in ['line', 'area']:
            base_options['interaction'] = {
                'intersect': False,
                'mode': 'index'
            }
            base_options['scales'] = self._build_scales_config(chart_type, chart_data)

            if chart_options.get('enable_zoom', False):
                base_options['plugins']['zoom'] = {
                    'pan': {'enabled': True, 'mode': 'x'},
                    'zoom': {'wheel': {'enabled': True}, 'mode': 'x'}
                }

        elif chart_type == 'scatter':
            base_options['scales'] = {
                'x': {
                    'type': 'linear',
                    'position': 'bottom',
                    'title': {'display': True, 'text': chart_data.get('x_axis', 'Category')}
                },
                'y': {
                    'title': {'display': True, 'text': chart_data.get('y_axis', 'Value')}
                }
            }

        elif chart_type == 'radar':
            base_options['scales'] = {
                'r': {
                    'beginAtZero': True,
                    'grid': {'color': '#f1f5f9'},
                    'pointLabels': {
                        'font': {'size': 11, 'family': 'Inter'},
                        'color': '#718096'
                    }
                }
            }

        return base_options

    def _build_tooltip_config(self, chart_type: str) -> Dict[str, Any]:
        """Build tooltip configuration for different chart types."""

        base_tooltip = {
            'enabled': True,
            'backgroundColor': '#ffffff',
            'titleColor': '#2d3748',
            'bodyColor': '#4a5568',
            'borderColor': '#e2e8f0',
            'borderWidth': 1,
            'cornerRadius': 6,
            'displayColors': True,
            'titleFont': {'size': 13, 'family': 'Inter', 'weight': '500'},
            'bodyFont': {'size': 12, 'family': 'Inter', 'weight': '400'},
            'padding': 12,
            'callbacks': {
                'label': f'PLACEHOLDER_{chart_type.upper()}_CALLBACK' if chart_type in ['pie', 'doughnut', 'scatter', 'bubble'] else 'PLACEHOLDER_DEFAULT_CALLBACK'
            }
        }

        return base_tooltip

    def _build_scales_config(self, chart_type: str, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build scales configuration for charts that need them."""

        if chart_type == 'horizontal_bar':
            return {
                'x': {
                    'beginAtZero': True,
                    'grid': {'color': '#f1f5f9', 'lineWidth': 1},
                    'ticks': {'color': '#718096', 'font': {'size': 11, 'family': 'Inter'}},
                    'title': {
                        'display': True,
                        'text': chart_data.get('y_axis', 'Value'),
                        'font': {'size': 12, 'family': 'Inter', 'weight': '500'},
                        'color': '#4a5568'
                    }
                },
                'y': {
                    'grid': {'color': '#f8fafc', 'lineWidth': 1},
                    'ticks': {'color': '#718096', 'font': {'size': 11, 'family': 'Inter'}, 'maxRotation': 0},
                    'title': {
                        'display': True,
                        'text': chart_data.get('x_axis', 'Category'),
                        'font': {'size': 12, 'family': 'Inter', 'weight': '500'},
                        'color': '#4a5568'
                    }
                }
            }
        else:
            # For bar, line, area charts
            return {
                'x': {
                    'grid': {'color': '#f8fafc', 'lineWidth': 1},
                    'ticks': {'color': '#718096', 'font': {'size': 11, 'family': 'Inter'}, 'maxRotation': 45},
                    'title': {
                        'display': True,
                        'text': chart_data.get('x_axis', 'Category'),
                        'font': {'size': 12, 'family': 'Inter', 'weight': '500'},
                        'color': '#4a5568'
                    }
                },
                'y': {
                    'beginAtZero': True,
                    'grid': {'color': '#f1f5f9', 'lineWidth': 1},
                    'ticks': {'color': '#718096', 'font': {'size': 11, 'family': 'Inter'}},
                    'title': {
                        'display': True,
                        'text': chart_data.get('y_axis', 'Value'),
                        'font': {'size': 12, 'family': 'Inter', 'weight': '500'},
                        'color': '#4a5568'
                    }
                }
            }

    def _inject_callback_functions(self, config_json: str, chart_type: str) -> str:
        """Inject JavaScript callback functions into the JSON configuration."""

        # Simple tooltip callbacks that work reliably
        if chart_type in ['pie', 'doughnut']:
            config_json = config_json.replace(
                '"label": "PLACEHOLDER_PIE_CALLBACK"',
                '''function(context) {
                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                    const percentage = ((context.parsed / total) * 100).toFixed(1);
                    return context.label + ": " + context.parsed.toLocaleString() + " (" + percentage + "%)";
                  }'''
            )
        elif chart_type in ['scatter', 'bubble']:
            config_json = config_json.replace(
                '"label": "PLACEHOLDER_SCATTER_CALLBACK"',
                '''function(context) {
                    return context.dataset.label + ": (" + context.parsed.x + ", " + context.parsed.y + ")";
                  }'''
            )
        else:
            config_json = config_json.replace(
                '"label": "PLACEHOLDER_DEFAULT_CALLBACK"',
                '''function(context) {
                    const value = context.parsed.y || context.parsed.x;
                    let formatted;
                    if (Math.abs(value) >= 1000000) {
                      formatted = (value / 1000000).toFixed(2) + "M";
                    } else if (Math.abs(value) >= 1000) {
                      formatted = (value / 1000).toFixed(2) + "K";
                    } else {
                      formatted = value.toLocaleString();
                    }
                    return context.dataset.label + ": " + formatted;
                  }'''
            )

        # Simple axis formatting (only for scales that exist)
        if chart_type in ['bar', 'line', 'area']:
            # Y-axis formatting for vertical charts
            config_json = config_json.replace(
                '"y": {\n        "beginAtZero": true,\n        "grid": {\n          "color": "#f1f5f9",\n          "lineWidth": 1\n        },\n        "ticks": {\n          "color": "#718096",\n          "font": {\n            "size": 11,\n            "family": "Inter"\n          }\n        }',
                '''      "y": {
                "beginAtZero": true,
                "grid": {
                  "color": "#f1f5f9",
                  "lineWidth": 1
                },
                "ticks": {
                  "color": "#718096",
                  "font": {
                    "size": 11,
                    "family": "Inter"
                  },
                  "callback": function(value) {
                    if (Math.abs(value) >= 1000000) {
                      return (value / 1000000).toFixed(1) + "M";
                    } else if (Math.abs(value) >= 1000) {
                      return (value / 1000).toFixed(1) + "K";
                    } else {
                      return value.toLocaleString();
                    }
                  }
                }'''
            )
        elif chart_type == 'horizontal_bar':
            # X-axis formatting for horizontal bars
            config_json = config_json.replace(
                '"x": {\n        "beginAtZero": true,\n        "grid": {\n          "color": "#f1f5f9",\n          "lineWidth": 1\n        },\n        "ticks": {\n          "color": "#718096",\n          "font": {\n            "size": 11,\n            "family": "Inter"\n          }\n        }',
                '''      "x": {
                "beginAtZero": true,
                "grid": {
                  "color": "#f1f5f9",
                  "lineWidth": 1
                },
                "ticks": {
                  "color": "#718096",
                  "font": {
                    "size": 11,
                    "family": "Inter"
                  },
                  "callback": function(value) {
                    if (Math.abs(value) >= 1000000) {
                      return (value / 1000000).toFixed(1) + "M";
                    } else if (Math.abs(value) >= 1000) {
                      return (value / 1000).toFixed(1) + "K";
                    } else {
                      return value.toLocaleString();
                    }
                  }
                }'''
            )

        return config_json

    # ========================================
    # UTILITY & FILE MANAGEMENT
    # ========================================

    def _get_file_stats(self, file_path: str) -> Dict[str, Any]:
        """Get file statistics."""
        try:
            stat = os.stat(file_path)
            return {
                'size_bytes': stat.st_size,
                'size_human': self._format_file_size(stat.st_size),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'absolute_path': os.path.abspath(file_path),
                'filename': os.path.basename(file_path)
            }
        except Exception as e:
            logger.error(f"Failed to get file stats: {e}")
            return {
                'filename': os.path.basename(file_path) if file_path else 'unknown',
                'error': str(e)
            }

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    # ========================================
    # DEBUG & LOGGING UTILITIES
    # ========================================

    def _debug_data_types(self, data: List[List], max_rows: int = 3) -> None:
        """Debug helper to show data types - helps diagnose issues."""
        if not self._should_log_debug():
            return

        logger.info("=== DATA TYPE DEBUGGING ===")
        for i, row in enumerate(data[:max_rows]):
            logger.info(f"Row {i}:")
            for j, value in enumerate(row):
                type_name = type(value).__name__
                is_numeric = self._is_numeric_value(value)
                converted = self._to_float(value) if is_numeric else 'N/A'
                logger.info(f"  Col {j}: {value} (type: {type_name}, numeric: {is_numeric}, converted: {converted})")
        logger.info("=== END DEBUGGING ===")

    def _should_log_debug(self) -> bool:
        """Check if debug logging should be enabled."""
        return logger.isEnabledFor(logging.INFO)