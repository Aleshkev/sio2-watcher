from typing import *
import datetime
import logging
import pathlib


from scrapper import *
from csv_handler import *


logger = logging.getLogger(__file__)


def main(file, url):
    extend_csv(pathlib.Path(file), dict(scrap(url)))


URL = "https://sio2.staszic.waw.pl/c/kolko-olimpijskie-201819/r/"
FILE = "data.csv"


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    from apscheduler.schedulers.blocking import BlockingScheduler
    scheduler = BlockingScheduler()

    @scheduler.scheduled_job('cron', hour=','.join(map(str,range(24))))
    def execute():
        main(FILE, URL)
    execute()
    scheduler.start()
