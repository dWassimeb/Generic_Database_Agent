"""
Enhanced database schemas and metadata for the Generic SQL Agent.
This file contains hardcoded advanced schema information.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Enhanced table schemas with detailed business context
TABLE_SCHEMAS = {
    "customers": {
        "description": "Customer information and demographics",
        "primary_key": "customer_id",
        "business_context": "Core customer data for CRM and analytics - contains customer demographics and contact information",
        "common_queries": ["customer analysis", "demographic breakdowns", "customer lookup", "customer counts"],
        "columns": {
            "customer_id": {
                "type": "INTEGER",
                "description": "Unique identifier for each customer",
                "is_primary_key": True,
                "business_meaning": "Primary key for customer records"
            },
            "name": {
                "type": "TEXT",
                "description": "Full name of the customer",
                "business_meaning": "Customer's complete name for identification and communication"
            },
            "email": {
                "type": "TEXT",
                "description": "Email address of the customer",
                "business_meaning": "Primary contact method for customer communication",
                "is_unique": True
            },
            "age": {
                "type": "INTEGER",
                "description": "Age of the customer in years",
                "business_meaning": "Customer age for demographic analysis and segmentation",
                "aggregatable": True
            },
            "city": {
                "type": "TEXT",
                "description": "City where the customer is located",
                "business_meaning": "Geographic location for regional analysis and shipping",
                "is_geographic": True
            }
        }
    },
    "orders": {
        "description": "Customer order transactions and details",
        "primary_key": "order_id",
        "business_context": "Core transaction data - contains all customer orders with products, quantities, and pricing",
        "common_queries": ["sales analysis", "order tracking", "revenue calculations", "customer purchase history"],
        "columns": {
            "order_id": {
                "type": "INTEGER",
                "description": "Unique identifier for each order",
                "is_primary_key": True,
                "business_meaning": "Primary key for order records"
            },
            "customer_id": {
                "type": "INTEGER",
                "description": "Reference to the customer who placed the order",
                "foreign_key": "customers.customer_id",
                "business_meaning": "Links order to customer information"
            },
            "product": {
                "type": "TEXT",
                "description": "Name of the product ordered",
                "business_meaning": "Product identification for inventory and sales analysis"
            },
            "quantity": {
                "type": "INTEGER",
                "description": "Number of units ordered",
                "business_meaning": "Quantity purchased for volume analysis",
                "aggregatable": True
            },
            "price": {
                "type": "REAL",
                "description": "Price per unit in USD",
                "business_meaning": "Unit price for revenue calculations",
                "aggregatable": True,
                "unit": "USD"
            },
            "order_date": {
                "type": "TEXT",
                "description": "Date when the order was placed (YYYY-MM-DD format)",
                "business_meaning": "Order timestamp for time-based analysis",
                "is_temporal": True,
                "date_format": "YYYY-MM-DD"
            }
        }
    },
    "products": {
        "description": "Product catalog and inventory information",
        "primary_key": "product_id",
        "business_context": "Product master data - contains product details, pricing, and inventory levels",
        "common_queries": ["product catalog", "inventory analysis", "pricing analysis", "category breakdowns"],
        "columns": {
            "product_id": {
                "type": "INTEGER",
                "description": "Unique identifier for each product",
                "is_primary_key": True,
                "business_meaning": "Primary key for product records"
            },
            "product_name": {
                "type": "TEXT",
                "description": "Name of the product",
                "business_meaning": "Product identification and catalog display"
            },
            "category": {
                "type": "TEXT",
                "description": "Product category classification",
                "business_meaning": "Product grouping for analysis and organization"
            },
            "price": {
                "type": "REAL",
                "description": "Current price of the product in USD",
                "business_meaning": "Product pricing for revenue and margin analysis",
                "aggregatable": True,
                "unit": "USD"
            },
            "stock_quantity": {
                "type": "INTEGER",
                "description": "Current inventory level",
                "business_meaning": "Available stock for inventory management",
                "aggregatable": True
            }
        }
    }
}

# Enhanced relationship definitions with join patterns
TABLE_RELATIONSHIPS = {
    "customers": {
        "joins_to": {
            "orders": {
                "join_key": "customer_id",
                "relationship": "one_to_many",
                "purpose": "Get customer's order history",
                "join_sql": "customers c JOIN orders o ON c.customer_id = o.customer_id"
            }
        }
    },
    "orders": {
        "joins_to": {
            "customers": {
                "join_key": "customer_id",
                "relationship": "many_to_one",
                "purpose": "Get customer information for orders",
                "join_sql": "orders o JOIN customers c ON o.customer_id = c.customer_id"
            },
            "products": {
                "join_key": "product_name",
                "relationship": "many_to_one",
                "purpose": "Get product details for orders",
                "join_sql": "orders o JOIN products p ON o.product = p.product_name"
            }
        }
    },
    "products": {
        "joins_to": {
            "orders": {
                "join_key": "product_name",
                "relationship": "one_to_many",
                "purpose": "Get order history for products",
                "join_sql": "products p JOIN orders o ON p.product_name = o.product"
            }
        }
    }
}

# Enhanced query patterns with business context
QUERY_PATTERNS = {
    "customer_analysis": {
        "keywords": ["customer", "client", "user", "demographics", "customer analysis"],
        "requires_tables": ["customers"],
        "key_columns": ["name", "email", "age", "city"],
        "common_joins": "customers c LEFT JOIN orders o ON c.customer_id = o.customer_id",
        "example_sql": "SELECT c.name, c.city, COUNT(o.order_id) as order_count FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id"
    },
    "sales_analysis": {
        "keywords": ["sales", "revenue", "orders", "transactions", "purchase"],
        "requires_tables": ["orders"],
        "key_columns": ["price", "quantity", "order_date"],
        "aggregations": ["SUM", "COUNT", "AVG"],
        "example_sql": "SELECT SUM(price * quantity) as total_revenue FROM orders"
    },
    "product_analysis": {
        "keywords": ["product", "inventory", "stock", "catalog", "category"],
        "requires_tables": ["products"],
        "key_columns": ["product_name", "category", "price", "stock_quantity"],
        "common_joins": "products p LEFT JOIN orders o ON p.product_name = o.product",
        "example_sql": "SELECT category, COUNT(*) as product_count, AVG(price) as avg_price FROM products GROUP BY category"
    },
    "temporal_analysis": {
        "keywords": ["time", "date", "period", "recent", "last", "daily", "monthly"],
        "requires_tables": ["orders"],
        "key_columns": ["order_date"],
        "common_filters": "WHERE order_date >= date('now', '-30 days')",
        "example_sql": "SELECT date(order_date) as order_day, COUNT(*) as daily_orders FROM orders WHERE order_date >= date('now', '-7 days') GROUP BY date(order_date)"
    },
    "geographic_analysis": {
        "keywords": ["city", "location", "geographic", "region", "area"],
        "requires_tables": ["customers"],
        "key_columns": ["city"],
        "common_joins": "customers c JOIN orders o ON c.customer_id = o.customer_id",
        "example_sql": "SELECT c.city, COUNT(o.order_id) as orders_count FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.city"
    }
}

# Business scenarios with SQL templates
BUSINESS_SCENARIOS = {
    "customer_ranking": {
        "description": "Rank customers by various metrics",
        "keywords": ["top customers", "best customers", "customer ranking", "highest"],
        "sql_template": """
        SELECT 
            c.name,
            c.city,
            COUNT(o.order_id) as order_count,
            SUM(o.price * o.quantity) as total_spent
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.name, c.city
        ORDER BY total_spent DESC
        LIMIT {limit}
        """,
        "required_tables": ["customers", "orders"]
    },
    "product_performance": {
        "description": "Analyze product sales performance",
        "keywords": ["product performance", "best selling", "popular products"],
        "sql_template": """
        SELECT 
            p.product_name,
            p.category,
            p.price,
            COALESCE(SUM(o.quantity), 0) as units_sold,
            COALESCE(SUM(o.price * o.quantity), 0) as revenue
        FROM products p
        LEFT JOIN orders o ON p.product_name = o.product
        GROUP BY p.product_id, p.product_name, p.category, p.price
        ORDER BY revenue DESC
        LIMIT {limit}
        """,
        "required_tables": ["products", "orders"]
    },
    "sales_trends": {
        "description": "Analyze sales trends over time",
        "keywords": ["sales trends", "daily sales", "monthly revenue", "time analysis"],
        "sql_template": """
        SELECT 
            date(order_date) as order_date,
            COUNT(*) as order_count,
            SUM(price * quantity) as daily_revenue
        FROM orders
        WHERE order_date >= date('now', '-{days} days')
        GROUP BY date(order_date)
        ORDER BY order_date
        """,
        "required_tables": ["orders"]
    },
    "inventory_status": {
        "description": "Check inventory levels and stock status",
        "keywords": ["inventory", "stock", "out of stock", "low stock"],
        "sql_template": """
        SELECT 
            product_name,
            category,
            stock_quantity,
            CASE 
                WHEN stock_quantity = 0 THEN 'Out of Stock'
                WHEN stock_quantity < 10 THEN 'Low Stock'
                ELSE 'In Stock'
            END as stock_status
        FROM products
        ORDER BY stock_quantity ASC
        LIMIT {limit}
        """,
        "required_tables": ["products"]
    },
    "customer_demographics": {
        "description": "Analyze customer demographics and distribution",
        "keywords": ["demographics", "age distribution", "customer distribution", "geographic"],
        "sql_template": """
        SELECT 
            city,
            COUNT(*) as customer_count,
            AVG(age) as avg_age,
            MIN(age) as youngest_customer,
            MAX(age) as oldest_customer
        FROM customers
        GROUP BY city
        ORDER BY customer_count DESC
        LIMIT {limit}
        """,
        "required_tables": ["customers"]
    }
}

def get_table_schema(table_name: str) -> Dict[str, Any]:
    """Get schema for a specific table."""
    return TABLE_SCHEMAS.get(table_name, {})

def get_all_table_schemas() -> Dict[str, Dict[str, Any]]:
    """Get all table schemas."""
    return TABLE_SCHEMAS

def get_table_relationships() -> Dict[str, Dict[str, Any]]:
    """Get table relationships."""
    return TABLE_RELATIONSHIPS

def get_query_patterns() -> Dict[str, Dict[str, Any]]:
    """Get query patterns."""
    return QUERY_PATTERNS

def get_business_scenarios() -> Dict[str, Dict[str, Any]]:
    """Get business scenarios."""
    return BUSINESS_SCENARIOS

def list_tables() -> List[str]:
    """List all available tables."""
    return list(TABLE_SCHEMAS.keys())

def get_column_info(table_name: str, column_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific column."""
    table_schema = TABLE_SCHEMAS.get(table_name, {})
    columns = table_schema.get('columns', {})
    return columns.get(column_name, {})

def get_foreign_keys(table_name: str) -> List[Dict[str, str]]:
    """Get foreign key relationships for a table."""
    foreign_keys = []
    table_schema = TABLE_SCHEMAS.get(table_name, {})
    columns = table_schema.get('columns', {})

    for col_name, col_info in columns.items():
        if 'foreign_key' in col_info:
            foreign_keys.append({
                'column': col_name,
                'references': col_info['foreign_key'],
                'description': col_info.get('business_meaning', '')
            })

    return foreign_keys

def get_aggregatable_columns(table_name: str) -> List[str]:
    """Get columns that can be aggregated (SUM, COUNT, AVG, etc.)."""
    table_schema = TABLE_SCHEMAS.get(table_name, {})
    columns = table_schema.get('columns', {})

    aggregatable = []
    for col_name, col_info in columns.items():
        if col_info.get('aggregatable', False):
            aggregatable.append(col_name)

    return aggregatable

def get_temporal_columns(table_name: str) -> List[str]:
    """Get columns that contain temporal/date information."""
    table_schema = TABLE_SCHEMAS.get(table_name, {})
    columns = table_schema.get('columns', {})

    temporal = []
    for col_name, col_info in columns.items():
        if col_info.get('is_temporal', False):
            temporal.append(col_name)

    return temporal

def get_geographic_columns(table_name: str) -> List[str]:
    """Get columns that contain geographic information."""
    table_schema = TABLE_SCHEMAS.get(table_name, {})
    columns = table_schema.get('columns', {})

    geographic = []
    for col_name, col_info in columns.items():
        if col_info.get('is_geographic', False):
            geographic.append(col_name)

    return geographic