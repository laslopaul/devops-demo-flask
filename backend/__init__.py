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
    text = pw.TextField(unique=True)
    date_added = pw.DateTimeField()


def db_init(recreate=False) -> bool:
    """Helper function to create the database table"""
    table_existed_before = False

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
            print("Empty fortune table recreated.")

    else:
        table_existed_before = True
        print("Fortune table already exists.")

    return table_existed_before


def import_data(filename: str) -> None:
    """Import fortunes from a file to the database"""
    with open(filename, encoding="utf8") as f:
        entries = f.read().split("%\n")

    i = 0
    entries_count = len(entries)
    start = time()
    for entry in entries:
        try:
            Fortune.create(text=entry, date_added=datetime.now())
        except pw.IntegrityError:
            wrn_color = "\033[93m"
            wrn_msg = "{}{}\t[WRN]\tEntry {} already exists in the database."
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            print(wrn_msg.format(wrn_color, timestamp, i))
            entries_count -= 1
        i += 1
        inf_color = "\033[0;37m"
        inf_msg = "{}{}\t[INF]\tProcessing entry {} of {} ({}%)"
        progress = format(i / len(entries) * 100, ".02f")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(inf_msg.format(inf_color, timestamp, i, len(entries), progress))

    end = time()
    elapsed = end - start
    elapsed_fmt = strftime("%H:%M:%S", gmtime(elapsed))
    speed = format(len(entries) / elapsed, ".02f")
    print(f"\nImported {entries_count} entries in {elapsed_fmt} ({speed} eps)")
    print(f"Duplicates found: {len(entries) - entries_count}")


def read_fortune() -> str:
    """Read a random fortune from the database"""
    with db.atomic():
        max_index = Fortune.select().count()
        fortune = Fortune.get_by_id(randint(1, max_index))
    return fortune.text
