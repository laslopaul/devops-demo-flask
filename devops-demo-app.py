from flask import Flask, render_template
from flask.cli import AppGroup
from os import getenv
import backend
import click

app = Flask(__name__)
db_cli = AppGroup("db")
db_conn_status = False
fortune = None


# Define CLI commands
@db_cli.command("init")
def init_tables():
    backend.db_init()


@db_cli.command("import")
@click.argument("filename")
def import_from_file(filename: str):
    backend.import_data(filename)
    backend.db.close()


@db_cli.command("reset")
def reset_tables():
    backend.db_init(recreate=True)


@db_cli.command("drop")
def drop():
    print("Dropping Fortune table...")
    backend.db.drop_tables([backend.Fortune])
    backend.db.close()
    print("Fortune table dropped.")


app.cli.add_command(db_cli)


# This hook ensures that a connection is opened to handle any queries
# generated by the request.
@app.before_request
def _db_connect():
    try:
        backend.db.connect()
        global fortune
        fortune = backend.read_fortune()
    except backend.pw.OperationalError as e:
        print(f"An error ocurred while connecting to the database: {e}")
    else:
        print("Successfully connected to the database.")
        global db_conn_status
        db_conn_status = True


# This hook ensures that the connection is closed when we've finished
# processing the request.
@app.teardown_request
def _db_close(exc):
    if not backend.db.is_closed():
        backend.db.close()


@app.route('/')
def index():
    return render_template(
        'index.html', fortune=fortune, connected=db_conn_status,
        app_version=getenv("APP_VERSION"), app_env=getenv("APP_ENV")
    )
