import collections
import pathlib
import csv

import matplotlib
import matplotlib.pyplot as plt


PAST = True
TRACK = False
VECTOR = False


if VECTOR:
    matplotlib.use('svg')


fig, ax = plt.subplots()

with pathlib.Path('data.csv').open(encoding='utf-8') as file:
    reader = csv.DictReader(file)
    rows = tuple(reader)

    tracked = ('Jonasz A.', 'Mikołaj B.', 'Janek S.')
    tracked_xs = collections.defaultdict(list)
    tracked_ys = collections.defaultdict(list)

    for i, row in enumerate(rows):
        v = tuple(sorted(map(int, filter(lambda x: len(x) > 0 and ' ' not in x, row.values())), reverse=True))
        if i != len(rows) - 1:
            if PAST:
                # TODO: Don't draw grey lines very close to each other, e.g. draw only one row of data per week.
                ax.plot(range(1, len(v) + 1), v, '-', color='lightgrey')
        else:
            ax.plot(range(1, len(v) + 1), v, '.-')

        for person in tracked:
            r = int(row[person])
            tracked_xs[person].append(1 + v.index(r))
            tracked_ys[person].append(r)

    if TRACK:
        for person in tracked:
            ax.plot(tracked_xs[person], tracked_ys[person], '--')

ax.set(xlabel="Miejsce w rankingu", ylabel="Punkty ~ Czas", title="Kółko Stasia")
ax.grid()

fig.savefig('docs/plot.' + 'svg' if VECTOR else 'png')

plt.show()
