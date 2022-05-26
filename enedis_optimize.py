#!/usr/bin/python3

import fileinput, datetime as dt

kWh = {"standard": 0.174, "low": 0.147, "high": 0.1841}
lows = [
    [(2, 7), (12.5, 15.5)],
    [(3, 8), (13.5, 16.5)],
    [(0, 8)],
    [(0, 6.5), (22.5, 24)]
]

data = [i.strip("\n").split(";") for i in fileinput.input()]
del data[:data.index(["Horodate", "Valeur"]) + 1]
data = [(dt.datetime.fromisoformat(i[0]), int(i[1])) for i in data]

cost = {"standard": [], "lows": []}
