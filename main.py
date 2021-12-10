import asyncio
import schedule as schedule
import time
from datetime import datetime

import pg_helper
import search_data


async def main():
    pg_helper.print_db_version()

    search_data.add_media_links_to_db()
    search_data.add_city_council_motion_to_db()


class Main:
    def __init__(self, name):
        self.name = name
        start_time = datetime.now().second
        print(f"[SCHEDULE] Starting new run. {datetime.now()}")
        asyncio.run(main())
        print(f"[SCHEDULE] Run finished in {datetime.now().second - start_time} seconds.")


class Schedule:
    # check db connection on startup
    if not pg_helper.print_db_version():
        print('[EXIT] No connection to database.')
        exit()

    print("Initiating schedule at " + str(datetime.now()))
    schedule.every().day.at("10:00").do(Main, 'Starting new run at 12:00')

    while True:
        schedule.run_pending()
        time.sleep(60)
