#!/usr/bin/python3

from calendar import month
import fileinput, datetime as dt, statistics as st

kWh = {"standard": .174, "low": .147, "high": .1841}
lows = [
    [(2, 7), (12.5, 15.5)],
    [(3, 8), (13.5, 16.5)],
    [(0, 8)],
    [(0, 6.5), (22.5, 24)]
]

print("Enedis Optimize\n")

data = [i.strip("\n").split(";") for i in fileinput.input()]
del data[:data.index(["Horodate", "Valeur"]) + 1]
data = [(dt.datetime.fromisoformat(i[0]), int(i[1])) for i in data]

cost = {"standard": {}, "lows": [{},] * len(lows)}
for i in data: cost["standard"][i[0]] = i[1] * kWh["standard"] / 1000
for i in range(len(lows)):
    for j in enumerate(data):
        if i > 0: delta = abs(j[1][0] - data[j[0] - 1][0])
        else: delta = abs(j[1][0] - data[j[0] + 1][0])
        cost["lows"][i][j[1][0]] = j[1][1] * kWh.values()[1:][any(k[0] <= j[1][0] - delta < k[1] for k in j)] / 1000

delta = (data[-1][0] - data[0][0]) / dt.timedelta(days = 365.2425 / 12)
print("Costs:")
print("\tStandard:", round((monthly_standard := sum(cost["standard"].values())) / delta, 2), "monthly")
print("\tLows:")
for i in enumerate(cost["lows"]): print("\t\t" + str(lows[i[0]]) + ":", round(sum(i[1].values()) / delta, 2), "monthly")
cost["lows"] = {i[0]: st.fmean([cost["lows"][j][i] for j in range(len(lows))]) for i in data}
print("\t\tAverage:", round((monthly_lows := sum(cost["lows"].values())) / delta, 2), "monthly")
print("\tDifference:", "{0:+.02f}".format((monthly_lows - monthly_standard) / delta), "monthly")
print()
