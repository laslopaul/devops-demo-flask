from flask.cli import AppGroup
import backend
import click
import logging

db_cli = AppGroup("db")


# Create logger
logger = logging.getLogger("devops_demo_cli")
logger.setLevel(logging.INFO)

# Create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    "[%(asctime)s] [%(process)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %z")

# Add formatter to console handler
ch.setFormatter(formatter)

# Add console handler to logger
logger.addHandler(ch)


# Define CLI commands
@db_cli.command("init")
def init_and_import():
    """Create the table and import initial set of entries"""
    try:
        backend.db.connect()
    except backend.pw.OperationalError as e:
        error_msg = f"MySQL error code {e.args[0]}: {e.args[1]}"
        logger.error(error_msg)
    else:
        if not backend.db_init():
            logger.info("Initializing the database...")
            logger.info("Importing file 'fortunes.txt'")
            backend.import_data("fortunes.txt")
            backend.db.close()
        else:
            logger.info("Database already initialized.")


@db_cli.command("import")
@click.argument("filename")
def import_from_file(filename: str):
    """Import entries from a specified file"""
    try:
        backend.db.connect()
    except backend.pw.OperationalError as e:
        error_msg = f"MySQL error code {e.args[0]}: {e.args[1]}"
        logger.error(error_msg)
    else:
        logger.info(f"Importing file '{filename}' to the database")
        backend.import_data(filename)
        backend.db.close()


@db_cli.command("reset")
def reset_tables():
    """Drop an existing table and create a new one"""
    try:
        backend.db.connect()
    except backend.pw.OperationalError as e:
        error_msg = f"MySQL error code {e.args[0]}: {e.args[1]}"
        logger.error(error_msg)
    else:
        backend.db_init(recreate=True)


@db_cli.command("drop")
def drop():
    """Drop an existing table"""
    try:
        backend.db.connect()
    except backend.pw.OperationalError as e:
        error_msg = f"MySQL error code {e.args[0]}: {e.args[1]}"
        logger.error(error_msg)
    else:
        logger.info("Dropping Fortune table...")
        backend.db.drop_tables([backend.Fortune])
        backend.db.close()
        logger.info("Fortune table dropped.")
