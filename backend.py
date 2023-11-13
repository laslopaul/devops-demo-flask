import peewee as pw
from datetime import datetime
from time import time, strftime, gmtime
from random import randint
from os import getenv
from hashlib import sha256
import logging

# Get Flask CLI logger
logger = logging.getLogger("devops_demo_cli")


try:
    sql_port = int(getenv("MYSQL_PORT"))
except TypeError:
    logger.warning("MySQL port is not defined, using default 3306")
    sql_port = 3306
finally:
    db = pw.MySQLDatabase(getenv("MYSQL_DB"), user=getenv("MYSQL_USER"),
                          password=getenv("MYSQL_PASSWD"),
                          host=getenv("MYSQL_HOST"),
                          port=sql_port)


class BaseModel(pw.Model):
    class Meta:
        database = db


class Fortune(BaseModel):
    fortune_id = pw.AutoField()
    text = pw.TextField()
    date_added = pw.DateTimeField()
    fortune_hash = pw.CharField(max_length=64, unique=True)


def db_init(recreate=False) -> bool:
    """Helper function to create the database table"""
    table_existed_before = False

    if not db.table_exists("fortune"):
        logger.info("Creating Fortune table...")
        with db.connection_context():
            db.create_tables([Fortune])
            logger.info("Fortune table created.")

    elif db.table_exists("fortune") and recreate:
        logger.info("Dropping Fortune table...")
        with db.connection_context():
            db.drop_tables([Fortune])
            db.create_tables([Fortune])
            logger.info("Empty fortune table recreated.")

    else:
        table_existed_before = True
        logger.info("Fortune table already exists.")

    return table_existed_before


def import_data(filename: str) -> None:
    """Import fortunes from a file to the database"""
    with open(filename, encoding="utf8") as f:
        entries = f.read().split("%\n")

    i = 0
    entries_count = len(entries)
    start = time()
    for entry in entries:
        m = sha256(entry.encode("UTF-8"))
        try:
            Fortune.create(text=entry, date_added=datetime.now(),
                           fortune_hash=m.hexdigest())
        except pw.IntegrityError:
            logger.warning(f"Entry {i} already exists in the database")
            entries_count -= 1
        i += 1
        inf_msg = "Processing entry {} of {} ({}%)"
        progress = format(i / len(entries) * 100, ".02f")
        logger.info(inf_msg.format(i, len(entries), progress))

    end = time()
    elapsed = end - start
    elapsed_fmt = strftime("%H:%M:%S", gmtime(elapsed))
    speed = format(len(entries) / elapsed, ".02f")
    logger.info(
        f"Imported {entries_count} entries in {elapsed_fmt} ({speed} eps)")
    logger.info(f"Duplicates found: {len(entries) - entries_count}")


def read_fortune() -> str:
    """Read a random fortune from the database"""
    with db.atomic():
        max_index = Fortune.select().count()
        fortune_id = randint(1, max_index)
        fortune = Fortune.get_by_id(fortune_id)
    logger.info(f"Read fortune #{fortune_id} from the database")
    return fortune.text
