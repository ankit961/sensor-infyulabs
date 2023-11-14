from flask_migrate import Migrate, init, migrate, upgrade
from app import app, db
from flask.cli import FlaskGroup
from alembic.config import Config
import model
import os
from dotenv import load_dotenv
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///default.db')
migrate = Migrate(app, db)
alembic_config = Config("migrations/alembic.ini")

alembic_config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URI)
# #Production
# alembic_config.set_main_option("sqlalchemy.url", "postgresql://infyulabs:infyulabs123@/sensors?host=/cloud_sql_proxy-instances=sensor-reading-404008:asia-south1:sensor=tcp:5432")

@app.cli.command("db_init")
def db_init():
    """Initialize the database."""
    init()

@app.cli.command("db_migrate")
def db_migrate():
    """Run the migrations."""
    migrate()

@app.cli.command("db_upgrade")
def db_upgrade():
    """Upgrade the database."""
    upgrade()
    
@app.cli.command("create_tables")
def create_tables():
    """Create tables in the database."""
    db.create_all()


if __name__ == '__main__':
    cli = FlaskGroup(app)
    cli()
