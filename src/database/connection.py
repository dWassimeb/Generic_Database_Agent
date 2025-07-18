# src/database/connection.py
import os
import sys
import platform
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from rich.console import Console
from dotenv import load_dotenv

# Load .env.local first (for host development), then .env (for Docker)
if os.path.exists('.env.local'):
    load_dotenv('.env.local')
else:
    load_dotenv()


class DatabaseConnection:
    def __init__(self):
        self.console = Console()
        self.config = {
            'host': os.getenv('DATABASE_HOST', 'localhost'),
            'database': os.getenv('DATABASE_NAME', 'france_services_db'),
            'user': os.getenv('DATABASE_USER', 'postgres'),
            'password': os.getenv('DATABASE_PASSWORD', 'password'),
            'port': os.getenv('DATABASE_PORT', '5432')
        }

        self.connection_string = (
            f"postgresql://{self.config['user']}:{self.config['password']}@"
            f"{self.config['host']}:{self.config['port']}/{self.config['database']}"
        )
        
        # Create engine but don't test connection yet
        self.engine = create_engine(self.connection_string)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_engine(self):
        """Get the SQLAlchemy engine, testing the connection first"""
        if not self.test_connection():
            sys.exit(1)
        return self.engine

    def get_session(self):
        """Get a new database session, testing the connection first"""
        if not self.test_connection():
            sys.exit(1)
        return self.SessionLocal()
        
    def test_connection(self):
        """Test the database connection and provide helpful error messages if it fails"""
        try:
            # Test the connection by executing a simple query
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except OperationalError as e:
            self.console.print(f"\n[bold red]❌ Erreur de connexion à PostgreSQL:[/bold red] {str(e)}")
            self.console.print("\n[bold yellow]Le serveur PostgreSQL n'est pas démarré ou n'accepte pas les connexions.[/bold yellow]")
            
            # Provide OS-specific instructions
            os_name = platform.system()
            self.console.print("\n[bold]Pour démarrer PostgreSQL:[/bold]")
            
            if os_name == "Darwin":  # macOS
                self.console.print("  [bold]macOS:[/bold]")
                self.console.print("  1. Si vous avez installé PostgreSQL via Homebrew:")
                self.console.print("     brew services start postgresql")
                self.console.print("  2. Si vous avez installé Postgres.app:")
                self.console.print("     Ouvrez l'application Postgres.app")
                
            elif os_name == "Linux":
                self.console.print("  [bold]Linux:[/bold]")
                self.console.print("  sudo systemctl start postgresql")
                self.console.print("  ou")
                self.console.print("  sudo service postgresql start")
                
            elif os_name == "Windows":
                self.console.print("  [bold]Windows:[/bold]")
                self.console.print("  1. Ouvrez les Services Windows (services.msc)")
                self.console.print("  2. Trouvez le service 'PostgreSQL' et démarrez-le")
                self.console.print("  ou")
                self.console.print("  net start postgresql")
            
            # Database creation instructions
            self.console.print("\n[bold]Si la base de données n'existe pas encore:[/bold]")
            self.console.print(f"  1. Connectez-vous à PostgreSQL: psql -U {self.config['user']}")
            self.console.print(f"  2. Créez la base de données: CREATE DATABASE {self.config['database']};")
            
            # Configuration instructions
            self.console.print("\n[bold]Pour configurer la connexion:[/bold]")
            self.console.print("  Créez un fichier .env à la racine du projet avec les variables suivantes:")
            self.console.print("  DATABASE_HOST=localhost")
            self.console.print(f"  DATABASE_NAME={self.config['database']}")
            self.console.print("  DATABASE_USER=votre_utilisateur")
            self.console.print("  DATABASE_PASSWORD=votre_mot_de_passe")
            self.console.print("  DATABASE_PORT=5432")
            
            return False