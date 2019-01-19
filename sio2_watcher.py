from typing import *
import datetime
import logging
import pathlib
import csv

import requests
import bs4


logger = logging.getLogger(__file__)


def simple_anonymize(name: str) -> str:
    """A very simple and stupid function to protect privacy of people whose names are scrapped."""
    base, *parts = name.split()

    # The most professional way.
    diminutives = {
        "Maksymilian": "Maks", "Maxymilian": "Max", "Joanna": "Asia", "Jakub": "Kuba", "Stanisław": "Staś",
        "Krzysztof": "Krzyś", "Antoni": "Antek", "Jan": "Janek", "Grzegorz": "Grześ", "Tomasz": "Tomek"
    }
    if base in diminutives:
        base = diminutives[base]
    shorted = [p[:2] if len(p) >= 2 and p[:2].lower() in ("ch", "sz", "cz", "dż", "rz") else p[:1] for p in parts]
    dotted = [p + ("." if len(parts[i]) > len(p) else "") for i, p in enumerate(shorted)]

    return " ".join([base] + dotted)


def scrap(url: str) -> Iterator[Tuple[str, int]]:
    """Yields tuples (name, points) scrapped from SIO2 ranking."""
    logger.info(f"Download {url}")
    page = requests.get(url).content.decode('utf-8')
    # page = pathlib.Path('test.html').read_text('utf-8')

    logger.info(f"Parse {len(page)} characters of HTML")
    soup = bs4.BeautifulSoup(page, 'html.parser')

    ranking, = [o for o in soup.find_all('table') if 'ranking' in o['class']]
    for row in ranking.find_all('tr'):
        if row.find_all('th'):
            continue
        name, = [str(o.get_text()).strip() for o in row.find_all('td') if 'full_name' in o['class']]
        points, = [int(o.get_text()) for o in row.find_all('td') if 'row_summary' in o['class']]
        yield simple_anonymize(name), points


def extend_csv(csv_file: pathlib.Path, new_row: Dict[str, int]):
    new_row: Dict[str, Any]
    new_row['TIMESTAMP'] = str(datetime.datetime.now())

    logger.info(f"Extend {csv_file}; new row with {len(new_row)} fields; timestamp of {new_row['TIMESTAMP']}")

    logger.info(f"Read {csv_file}")
    fields = {'TIMESTAMP'} | set(new_row.keys())
    if csv_file.exists() and csv_file.read_text().strip() != '':
        with csv_file.open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fields |= set(reader.fieldnames)
            table = list(reader)
    else:
        table = []

    fields = ['TIMESTAMP'] + sorted(list(fields - {'TIMESTAMP'}))

    logger.info(f"Write to {csv_file.absolute()}; {len(fields)} fields, {len(table) + 1} rows")
    with csv_file.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in table + [new_row]:
            writer.writerow(row)


def main(file, url):
    extend_csv(pathlib.Path(file), dict(scrap(url)))


URL = "https://sio2.staszic.waw.pl/c/kolko-olimpijskie-201819/r/"
FILE = "data.csv"


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    from apscheduler.schedulers.blocking import BlockingScheduler
    scheduler = BlockingScheduler()

    @scheduler.scheduled_job('interval', hours=1)
    def execute():
        main(FILE, URL)
    execute()
    scheduler.start()
