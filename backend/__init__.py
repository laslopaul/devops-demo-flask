import peewee as pw
from datetime import datetime
from time import time, strftime, gmtime
from random import randint

db = pw.SqliteDatabase("fortunes.db")


class BaseModel(pw.Model):
    class Meta:
        database = db


class Fortune(BaseModel):
    fortune_id = pw.AutoField()
    text = pw.TextField()
    date_added = pw.DateTimeField()


def db_init(recreate=False) -> None:
    """Helper function to create the database table"""
    if not db.table_exists("fortune"):
        print("Creating Fortune table...")
        with db.connection_context():
            db.create_tables([Fortune])
            print("Fortune table created.")

    elif db.table_exists("fortune") and recreate:
        print("Dropping Fortune table...")
        with db.connection_context():
            db.drop_tables([Fortune])
            db.create_tables([Fortune])
            print("Fortune table recreated.")

    else:
        print("Fortune table already exists.")


def import_data(filename: str) -> None:
    """Import fortunes from a file to the database"""
    with open(filename, encoding="utf8") as f:
        entries = f.read().split("%\n")

    i = 0
    start = time()
    for entry in entries:
        Fortune.create(text=entry, date_added=datetime.now())
        i += 1
        progress = format(i / len(entries) * 100, ".02f")
        print(f"Import entry {i} of {len(entries)} ({progress}%)")

    end = time()
    elapsed = end - start
    elapsed_fmt = strftime("%H:%M:%S", gmtime(elapsed))
    speed = format(len(entries) / elapsed, ".02f")
    print(f"Imported {len(entries)} entries in {elapsed_fmt} ({speed} eps)")


def read_fortune() -> str:
    """Read a random fortune from the database"""
    with db.atomic():
        max_index = Fortune.select().count()
        fortune = Fortune.get_by_id(randint(1, max_index))
    return fortune.text
