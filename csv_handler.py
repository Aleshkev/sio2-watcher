from typing import *
import logging
import pathlib
import datetime
import csv


__all__ = ['extend_csv']


logger = logging.getLogger('csv_handler')


def extend_csv(csv_file: pathlib.Path, new_row: Dict[str, int]):
    new_row: Dict[str, Any] = new_row
    new_row['TIMESTAMP'] = str(datetime.datetime.now())

    logger.info(f"Extend {csv_file}; new row with {len(new_row)} fields; timestamp of {new_row['TIMESTAMP']}")

    logger.info(f"Read {csv_file}")
    fields = {'TIMESTAMP'} | set(new_row.keys())
    if csv_file.exists() and csv_file.read_text(encoding='utf-8').strip() != '':
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
