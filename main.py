"""
Generic SQL Agent - Main Entry Point
Clean, efficient LangGraph implementation for generic SQL databases
"""

import sys
import logging
from pathlib import Path
from core.agent import GenericSQLGraphAgent
from database.connection import generic_db_connection
from config.settings import DATABASE_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function with proper LangGraph structure."""

    # ===== CONFIGURATION =====
    VERBOSE_MODE = True  # Set to False for clean output
    # =========================

    # Command line overrides
    if "--verbose" in sys.argv or "-v" in sys.argv:
        verbose = True
    elif "--quiet" in sys.argv or "-q" in sys.argv:
        verbose = False
    else:
        verbose = VERBOSE_MODE

    print("🚀 Generic SQL Agent Starting...")
    if verbose:
        print("🔍 Verbose mode - showing full LangGraph workflow")
        print("💡 Architecture: Agent (reasoning) + Tools (execution) + Router (decisions)")
    else:
        print("🤫 Quiet mode - clean output only")

    # Check if database is initialized
    print("🔌 Testing database connection...")

    # Check if database file exists
    db_path = Path(DATABASE_CONFIG.db_path)
    if not db_path.exists():
        print("❌ Database not found!")
        print("💡 Please initialize the database first:")
        print("   python database/initialize_db.py")
        return

    try:
        if generic_db_connection.test_connection():
            print("✅ Database connection successful!")

            # Show available tables
            tables = generic_db_connection.list_tables()
            print(f"📊 Available tables: {tables}")

            if not tables:
                print("⚠️  No tables found in database. Please run initialization script:")
                print("   python database/initialize_db.py")
                return

        else:
            print("❌ Database connection failed!")
            print("💡 Please check database configuration and try:")
            print("   python database/initialize_db.py --reset")
            return
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print("💡 Try reinitializing the database:")
        print("   python database/initialize_db.py --reset")
        return

    print("Type 'exit' to quit, 'help' for assistance")
    if verbose:
        print("💡 Tip: You'll see the complete AI reasoning process")
        print("💡 Use 'python main.py --quiet' to disable verbose mode")
    else:
        print("💡 Use 'python main.py --verbose' to see AI reasoning process")
    print()

    # Create the LangGraph agent
    agent = GenericSQLGraphAgent(verbose=verbose)

    # Main interaction loop
    while True:
        try:
            user_input = input("📝 Your question: ").strip()

            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break

            if user_input.lower() == 'help':
                show_help()
                continue

            if user_input.lower() == 'tables':
                show_tables()
                continue

            if user_input.lower().startswith('schema '):
                table_name = user_input[7:].strip()
                show_table_schema(table_name)
                continue

            if not user_input:
                print("❌ Please enter a question.")
                continue

            print("\n🔄 Processing your question through LangGraph...")
            response = agent.process_question(user_input)
            print(f"\n{response}\n")
            print("-" * 80)

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            print(f"\n❌ An error occurred: {e}")
            print("Please try again.\n")

def show_help():
    """Show help information."""
    print("""
🔮 Generic SQL Agent - Help

**Available Commands:**
• `tables` - List all available tables
• `schema <table_name>` - Show schema for a specific table
• `help` - Show this help message
• `exit` - Exit the application

**Example Questions:**
• "Show me all customers"
• "How many orders do we have?"
• "What are the top 5 products by price?"
• "Show me customers from New York"
• "List all orders with their customer names"

**Features:**
• Natural language to SQL conversion
• Automatic CSV export of results
• Interactive visualizations
• Safe query execution (SELECT only)
• Smart error handling

**Tips:**
• Be specific about what data you want
• Use natural language - no SQL knowledge needed
• Ask for counts, comparisons, or filtered data
• Results are automatically limited to 1000 rows for safety
    """)

def show_tables():
    """Show available tables."""
    try:
        tables = generic_db_connection.list_tables()
        if tables:
            print("📊 Available Tables:")
            for table in tables:
                print(f"  • {table}")

                # Show row count
                try:
                    result = generic_db_connection.execute_query_with_names(f"SELECT COUNT(*) FROM {table}")
                    if result['data']:
                        count = result['data'][0][0]
                        print(f"    ({count:,} rows)")
                except:
                    print("    (row count unavailable)")
        else:
            print("❌ No tables found in database")
    except Exception as e:
        print(f"❌ Error listing tables: {e}")

def show_table_schema(table_name: str):
    """Show schema for a specific table."""
    try:
        schema = generic_db_connection.get_table_schema(table_name)
        if schema:
            print(f"📋 Schema for table: {table_name}")
            print(f"Columns:")
            for col_name, col_info in schema.get('columns', {}).items():
                col_type = col_info.get('type', 'UNKNOWN')
                nullable = "NULL" if col_info.get('nullable', True) else "NOT NULL"
                print(f"  • {col_name} ({col_type}) {nullable}")

                # Show default value if available
                default = col_info.get('default')
                if default:
                    print(f"    Default: {default}")
        else:
            print(f"❌ Table '{table_name}' not found")
            print("💡 Use 'tables' command to see available tables")
    except Exception as e:
        print(f"❌ Error getting schema: {e}")

if __name__ == "__main__":
    main()