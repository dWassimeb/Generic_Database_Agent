"""
Database initialization script - Initialize database from CSV files
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.connection import generic_db_connection
from database.csv_manager import csv_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize the database from CSV files."""
    print("🚀 Initializing Generic SQL Agent Database...")

    try:
        # Check if CSV directory exists
        csv_dir = Path("database/csv_files")
        if not csv_dir.exists():
            print(f"📁 Creating CSV directory: {csv_dir}")
            csv_dir.mkdir(parents=True, exist_ok=True)

            # Create sample CSV files for demonstration
            create_sample_csv_files(csv_dir)

        # Initialize CSV manager
        print("📊 Analyzing CSV files...")
        csv_files = list(csv_dir.glob("*.csv"))
        print(f"Found {len(csv_files)} CSV files: {[f.name for f in csv_files]}")

        if not csv_files:
            print("⚠️  No CSV files found. Please add CSV files to the database/csv_files directory.")
            return False

        # Initialize database connection
        print("🔌 Connecting to database...")
        if not generic_db_connection.test_connection():
            print("❌ Database connection failed")
            return False

        # Import CSV files to database
        print("📥 Importing CSV files to database...")
        success = generic_db_connection.initialize_from_csv_directory(str(csv_dir))

        if success:
            print("✅ Database initialized successfully!")

            # List tables
            tables = generic_db_connection.list_tables()
            print(f"📋 Created {len(tables)} tables: {tables}")

            # Show sample data
            for table in tables[:3]:  # Show first 3 tables
                print(f"\n📊 Sample data from {table}:")
                try:
                    result = generic_db_connection.execute_query_with_names(f"SELECT * FROM {table} LIMIT 3")
                    if result['data']:
                        print(f"   Columns: {result['columns']}")
                        for i, row in enumerate(result['data']):
                            print(f"   Row {i+1}: {row}")
                    else:
                        print("   No data found")
                except Exception as e:
                    print(f"   Error: {e}")

            return True
        else:
            print("❌ Database initialization failed")
            return False

    except Exception as e:
        print(f"❌ Initialization error: {e}")
        logger.error(f"Database initialization failed: {e}")
        return False

def create_sample_csv_files(csv_dir: Path):
    """Create sample CSV files for demonstration."""
    print("📝 Creating sample CSV files...")

    import pandas as pd

    # Sample customers data
    customers_data = {
        'customer_id': [1, 2, 3, 4, 5],
        'name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson'],
        'email': ['john@example.com', 'jane@example.com', 'bob@example.com', 'alice@example.com', 'charlie@example.com'],
        'age': [25, 30, 35, 28, 42],
        'city': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
    }

    # Sample orders data
    orders_data = {
        'order_id': [101, 102, 103, 104, 105, 106, 107, 108],
        'customer_id': [1, 1, 2, 3, 2, 4, 5, 3],
        'product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones', 'Tablet', 'Phone', 'Webcam'],
        'quantity': [1, 2, 1, 1, 1, 1, 1, 1],
        'price': [999.99, 25.50, 79.99, 299.99, 89.99, 399.99, 699.99, 49.99],
        'order_date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19', '2024-01-20', '2024-01-21', '2024-01-22']
    }

    # Sample products data
    products_data = {
        'product_id': [1, 2, 3, 4, 5, 6, 7, 8],
        'product_name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones', 'Tablet', 'Phone', 'Webcam'],
        'category': ['Electronics', 'Accessories', 'Accessories', 'Electronics', 'Accessories', 'Electronics', 'Electronics', 'Accessories'],
        'price': [999.99, 25.50, 79.99, 299.99, 89.99, 399.99, 699.99, 49.99],
        'stock_quantity': [50, 200, 150, 75, 100, 30, 25, 80]
    }

    # Create CSV files
    pd.DataFrame(customers_data).to_csv(csv_dir / 'customers.csv', index=False)
    pd.DataFrame(orders_data).to_csv(csv_dir / 'orders.csv', index=False)
    pd.DataFrame(products_data).to_csv(csv_dir / 'products.csv', index=False)

    print(f"✅ Created sample CSV files: customers.csv, orders.csv, products.csv")

def reset_database():
    """Reset the database by removing the database file."""
    db_path = Path("user_data/database.db")
    if db_path.exists():
        db_path.unlink()
        print(f"🗑️  Removed existing database: {db_path}")

    # Also clear any existing connection
    if generic_db_connection.connection:
        generic_db_connection.close()

def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Initialize Generic SQL Agent Database")
    parser.add_argument('--reset', action='store_true', help='Reset database before initialization')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if args.reset:
        print("🔄 Resetting database...")
        reset_database()

    success = initialize_database()

    if success:
        print("\n🎉 Database is ready!")
        print("You can now run the agent with: python app.py")
        print("Or test with: python main.py")
        exit(0)
    else:
        print("\n❌ Database initialization failed!")
        exit(1)

if __name__ == "__main__":
    main()