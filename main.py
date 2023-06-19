import sys

from database.seeder import Seeder
from app.consumer import consumer

if __name__ == "__main__":
    try:
        if "seed" in sys.argv:
            seeder = Seeder()
            seeder.seed()
            seeder.close()
        else:
            consumer()
    except KeyboardInterrupt:
        print("Exiting...")
