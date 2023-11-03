from flask_migrate import Migrate, init, migrate, upgrade
from app import app, db
from flask.cli import FlaskGroup
from alembic.config import Config
import model

migrate = Migrate(app, db)
alembic_config = Config("migrations/alembic.ini")

alembic_config.set_main_option("sqlalchemy.url", "postgresql://infyulabs:infyulabs123@localhost:5432/sensors")


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
