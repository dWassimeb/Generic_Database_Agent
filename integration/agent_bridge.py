"""
Simple Agent Bridge with Global Token Tracking - PostgreSQL Support
"""

import sys
import os
import logging
from typing import Dict, Any, Optional
import traceback
from datetime import datetime

# Ensure we can import from the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# Add both current directory and project root to Python path
for path in [project_root, current_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

logger = logging.getLogger(__name__)

class TelmiAgentBridge:
    """Simple bridge with global token tracking - PostgreSQL support."""

    def __init__(self):
        self.agent = None
        self.connection_tested = False
        self.last_error = None
        self._setup_logging()
        self._attempt_initial_setup()

    def _setup_logging(self):
        """Configure logging for better debugging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def _attempt_initial_setup(self):
        """Attempt initial setup to identify issues early."""
        try:
            # Test imports first
            self._test_imports()
            logger.info("✅ All imports successful")
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"❌ Initial setup failed: {e}")

    def _test_imports(self):
        """Test if we can import the required modules."""
        try:
            # Test core agent import
            from core.agent import GenericSQLGraphAgent
            logger.info("✅ Core agent import successful")

            # Test POSTGRESQL database import (FIXED)
            from src.database.connection import database_connection
            logger.info("✅ Database connection import successful")

            return True

        except ImportError as e:
            error_msg = f"Import failed: {e}"
            logger.error(f"❌ {error_msg}")
            raise ImportError(error_msg)
        except Exception as e:
            logger.error(f"❌ Unexpected import error: {e}")
            raise

    def initialize_agent(self, verbose: bool = False) -> bool:
        """Initialize the LangGraph agent."""
        try:
            logger.info("🔧 Initializing Generic SQL LangGraph Agent...")

            # Import the agent class
            from core.agent import GenericSQLGraphAgent

            # 🔥 NO SHARED LLM NEEDED - Just create agent normally
            self.agent = GenericSQLGraphAgent(verbose=verbose)

            if self.agent is not None:
                logger.info("✅ Agent initialized successfully")
                return True
            else:
                error_msg = "Agent initialization returned None"
                logger.error(f"❌ {error_msg}")
                self.last_error = error_msg
                return False

        except ImportError as e:
            error_msg = f"Cannot import required modules: {e}"
            logger.error(f"❌ {error_msg}")
            self.last_error = error_msg
            return False

        except Exception as e:
            error_msg = f"Agent initialization failed: {e}"
            logger.error(f"❌ {error_msg}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.last_error = error_msg
            return False

    def test_database_connection(self) -> Dict[str, Any]:
        """Test the PostgreSQL database connection."""
        try:
            logger.info("🔌 Testing PostgreSQL database connection...")

            # Import the POSTGRESQL connection (FIXED)
            from src.database.connection import database_connection

            # Test the connection
            if database_connection.test_connection():
                self.connection_tested = True
                logger.info("✅ PostgreSQL database connection successful")

                # Test tables
                tables = database_connection.list_tables()
                logger.info(f"✅ Found {len(tables)} tables: {tables}")

                return {
                    'success': True,
                    'message': f'PostgreSQL connection successful - {len(tables)} tables found',
                    'status': 'connected',
                    'tables': tables
                }
            else:
                error_msg = 'PostgreSQL database connection failed'
                logger.error(f"❌ {error_msg}")
                return {
                    'success': False,
                    'message': error_msg,
                    'status': 'disconnected',
                    'suggestion': 'Check PostgreSQL server and run: poetry run init-db'
                }

        except ImportError as e:
            error_msg = f'PostgreSQL database module import failed: {e}'
            logger.error(f"❌ {error_msg}")
            return {
                'success': False,
                'message': error_msg,
                'status': 'import_error',
                'suggestion': 'Check if src/database/ directory and modules exist'
            }
        except Exception as e:
            error_msg = f'PostgreSQL database connection error: {e}'
            logger.error(f"❌ {error_msg}")
            return {
                'success': False,
                'message': error_msg,
                'status': 'error',
                'suggestion': 'Check PostgreSQL configuration and .env file'
            }

    def process_question(self, user_question: str, username: str = "unknown") -> Dict[str, Any]:
        """🔥 Process user question with SIMPLE global token tracking."""
        try:
            logger.info(f"🤔 Processing question: {user_question[:50]}...")

            # Ensure agent is initialized
            if self.agent is None:
                logger.info("🔧 Agent not initialized, attempting to initialize...")
                if not self.initialize_agent(verbose=False):
                    return {
                        'success': False,
                        'response': f"""❌ **Agent Initialization Failed**

**Issue:** Could not initialize the Generic SQL LangGraph agent.

**Last Error:** {self.last_error or 'Unknown error'}

**Debug Steps:**
1. Check if CLI agent works: `python main.py`
2. Check PostgreSQL connection: `poetry run python test_schema_mapping.py`
3. Verify all dependencies: `poetry install`
4. Initialize database: `poetry run init-db`""",
                        'error': 'Agent not initialized'
                    }

            # Test database connection if not already tested
            if not self.connection_tested:
                logger.info("🔌 Testing database connection...")
                db_test = self.test_database_connection()
                if not db_test['success']:
                    return {
                        'success': False,
                        'response': f"""❌ **PostgreSQL Database Connection Failed**

**Issue:** {db_test['message']}
**Status:** {db_test['status']}
**Suggestion:** {db_test.get('suggestion', 'Check PostgreSQL configuration')}

**Quick Fix:**
1. Start PostgreSQL server
2. Run: `poetry run generate-data`
3. Run: `poetry run init-db`""",
                        'error': db_test['message']
                    }

            # 🔥 START GLOBAL TOKEN TRACKING SESSION
            try:
                # Import with proper path handling
                import sys
                import os
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(current_dir)

                # Add paths to ensure import works
                for path in [current_dir, project_root]:
                    if path not in sys.path:
                        sys.path.insert(0, path)

                from llm.global_token_tracker import global_token_tracker

                # Start tracking session
                session_id = global_token_tracker.start_session(user_question, username)
                logger.info(f"🔥 Started global token tracking session for user: {username}")

            except ImportError:
                logger.warning("⚠️  Global token tracker not available, proceeding without tracking")
                session_id = None

            # Process question through LangGraph
            logger.info("🧠 Starting direct LangGraph processing...")

            # Use the agent to process the question
            response = self.agent.process_question(user_question)

            # 🔥 END TOKEN TRACKING AND GET SUMMARY
            if session_id:
                try:
                    token_summary = global_token_tracker.end_session(session_id)
                    csv_file = global_token_tracker.export_session_to_csv(session_id)

                    logger.info(f"🔥 Token tracking completed: {token_summary}")

                    return {
                        'success': True,
                        'response': response,
                        'token_usage': token_summary,
                        'token_report_file': csv_file
                    }
                except Exception as token_error:
                    logger.warning(f"⚠️  Token tracking end failed: {token_error}")

            # Return response without token tracking if tracking failed
            logger.info("✅ LangGraph processing completed")
            return {
                'success': True,
                'response': response
            }

        except Exception as e:
            error_msg = f"Question processing failed: {e}"
            logger.error(f"❌ {error_msg}")
            logger.error(f"Traceback: {traceback.format_exc()}")

            # Try to end token tracking session if it exists
            try:
                if 'session_id' in locals() and session_id:
                    token_summary = global_token_tracker.end_session(session_id)
                    csv_file = global_token_tracker.export_session_to_csv(session_id)
                else:
                    token_summary = None
                    csv_file = None
            except:
                token_summary = None
                csv_file = None

            return {
                'success': False,
                'response': f"""❌ **Processing Error**

**Issue:** {str(e)}
**Type:** {type(e).__name__}

**Debug Info:** Check the terminal for full error details.

**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""",
                'error': str(e),
                'token_usage': token_summary,
                'token_report_file': csv_file
            }

    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the agent and database connection."""
        status = {
            'agent_initialized': self.agent is not None,
            'database_tested': self.connection_tested,
            'ready': False,
            'last_error': self.last_error,
            'project_structure_ok': self._check_project_structure(),
            'timestamp': datetime.now().isoformat(),
            'threading_disabled': True,
            'mode': 'direct_execution'
        }

        # Test database connection if agent is initialized
        if status['agent_initialized']:
            if not status['database_tested']:
                db_test = self.test_database_connection()
                status['database_connected'] = db_test['success']
                status['database_message'] = db_test['message']
                status['database_suggestion'] = db_test.get('suggestion', '')
            else:
                status['database_connected'] = True
                status['database_message'] = 'Connected and tested'

            status['ready'] = status['agent_initialized'] and status.get('database_connected', False)
        else:
            # Try to initialize if not already done
            status['initialization_attempted'] = self.initialize_agent(verbose=False)
            if status['initialization_attempted']:
                return self.get_agent_status()  # Recursive call after initialization

        return status

    def _check_project_structure(self) -> bool:
        """Check if the required project structure exists."""
        required_dirs = ['core', 'src/database', 'tools']
        required_files = ['main.py', 'core/agent.py', 'src/database/connection.py']

        missing = []

        # Check directories
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                missing.append(f"Directory: {dir_name}/")

        # Check files
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing.append(f"File: {file_path}")

        if missing:
            logger.warning(f"❌ Missing project components: {', '.join(missing)}")
            return False

        logger.info("✅ Project structure looks good")
        return True

# Global instance
telmi_bridge = TelmiAgentBridge()