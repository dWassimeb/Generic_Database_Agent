"""
Generic SQL Agent - Main Entry Point
Clean, efficient LangGraph implementation for PostgreSQL databases
"""

import sys
import logging
from pathlib import Path
from core.agent import GenericSQLGraphAgent

# Import from new database location
from src.database.connection import database_connection

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

    try:
        if database_connection.test_connection():
            print("✅ Database connection successful!")

            # Show available tables
            tables = database_connection.list_tables()
            print(f"📊 Available tables: {tables}")

            if not tables:
                print("⚠️  No tables found in database. Please run initialization script:")
                print("   poetry run init-db")
                print("   or run: python scripts/init_db.py")
                return

        else:
            print("❌ Database connection failed!")
            print("💡 Please check database configuration and try:")
            print("   1. Make sure PostgreSQL is running")
            print("   2. Check your .env configuration")
            print("   3. Run: poetry run init-db")
            return
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print("💡 Try initializing the database:")
        print("   1. Start PostgreSQL server")
        print("   2. Run: poetry run generate-data")
        print("   3. Run: poetry run init-db")
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

            if not user_input:
                print("⚠️  Please enter a question or 'help' for assistance")
                continue

            # Process the question through LangGraph
            print()  # Add spacing
            response = agent.process_question(user_input)
            print(f"\n📋 Response:\n{response}")
            print()  # Add spacing

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            print(f"❌ Error: {e}")
            print("💡 Try rephrasing your question or type 'help' for assistance")


def show_help():
    """Display help information."""
    help_text = """
📚 Generic SQL Agent Help

🎯 Purpose: Ask questions about your data in natural language

📋 Example Questions:
   • "List all tables"
   • "Show me the first 10 records from demandes table"
   • "How many requests are there in total?"
   • "Show me the top 5 France Services offices by number of requests"
   • "What are the most common types of services requested?"
   • "Show me statistics for the last month"

🔧 Commands:
   • 'help' - Show this help
   • 'exit' - Quit the program
   • '--verbose' - Enable detailed workflow output
   • '--quiet' - Disable detailed output

💡 Tips:
   • Be specific about what data you want
   • Ask for table schemas if you need to understand the structure
   • The agent will generate and execute SQL queries safely
   • Results are automatically exported to CSV files when applicable

🗄️ Database Info:
   • Type: PostgreSQL
   • Tables: France Services data (offices, users, requests, etc.)
   • All queries are read-only for safety
"""
    print(help_text)


if __name__ == "__main__":
    main()