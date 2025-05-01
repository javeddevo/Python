from app import create_app
from app.database import init_db
import click

app = create_app()

@app.cli.command("init-db")
def init_db_command():
    """Initialize the database with data from sample.yaml."""
    init_db(app)
    click.echo("Database initialized.")

if __name__ == '__main__':
    app.run(debug=True)