import pathlib
from typing import *
import logging

import bs4
import requests


__all__ = ['scrap']


logger = logging.getLogger('scrapper')


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
    # pathlib.Path('test.html').write_text(page, encoding='utf-8')

    logger.info(f"Parse {len(page)} characters of HTML")
    soup = bs4.BeautifulSoup(page, 'html.parser')

    ranking, = [o for o in soup.find_all('table') if 'ranking' in o['class']]
    for row in ranking.find_all('tr'):
        if row.find_all('th'):
            continue
        name, = [str(o.get_text()).strip() for o in row.find_all('td') if 'full_name' in o['class']]
        points, = [int(o.get_text()) for o in row.find_all('td') if 'row_summary' in o['class']]
        yield simple_anonymize(name), points
