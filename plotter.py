import collections
import pathlib
import csv

import matplotlib
import matplotlib.pyplot as plt

PAST = True  # Draw not-newest results with grey lines.
TRACK = True  # Draw dotted colored lines between tracked people's scores.
ANNOTATE = True  # Annotate tracked people's scores.
VECTOR = True  # Save as vector (PNG if False).

if VECTOR:
    matplotlib.use('svg')

fig, ax = plt.subplots()


assigned = []


def find_position(x, y):
    # An ugly bodge to assign positions for labels.
    x += 8
    y += 40
    changed = True
    while changed:
        changed = False
        for u, v in assigned:
            if abs(u - x) > 5 or abs(y - v) > 400:
                continue
            y += 50
            changed = True
    assigned.append((x, y))
    return x, y


with pathlib.Path('data.csv').open(encoding='utf-8') as file:
    reader = csv.DictReader(file)
    rows = tuple(reader)

    tracked = ('Jonasz A.', 'Mikołaj B.', 'Kuba B.', 'Antek D.')
    tracked_xs = collections.defaultdict(list)
    tracked_ys = collections.defaultdict(list)

    for i, row in enumerate(rows):
        last = i == len(rows) - 1

        v = tuple(sorted(map(int, filter(lambda x: len(x) > 0 and ' ' not in x, row.values())), reverse=True))
        if not last and PAST:
            # TODO: Don't draw grey lines very close to each other, e.g. draw only one row of data per week.
            ax.plot(range(1, len(v) + 1), v, '-', color='lightgrey')
        if last:
            ax.plot(range(1, len(v) + 1), v, '.-')

        for person in tracked:
            r = int(row[person])
            tracked_xs[person].append(1 + v.index(r))
            tracked_ys[person].append(r)

            if last and ANNOTATE:
                xy = (1 + v.index(r), r)
                ax.annotate(f"{person}", xy=xy, xycoords='data', ha='center', xytext=find_position(*xy),
                            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.2", shrinkB=3))

    if TRACK:
        for person in tracked:
            ax.plot(tracked_xs[person], tracked_ys[person], '--')

ax.set(xlabel="Miejsce w rankingu", ylabel="Punkty ~ Czas", title="Kółko Stasia")
ax.grid()

fig.savefig('docs/plot.' + 'svg' if VECTOR else 'png')

plt.show()
