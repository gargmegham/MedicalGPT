import sys

from app.consumer import consumer
from app.globals import DB
from database.seeder import Seeder

if __name__ == "__main__":
    try:
        DB.start()
        if "seed" in sys.argv:
            seeder = Seeder()
            seeder.seed()
            seeder.close()
        else:
            consumer()
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        DB.close()
