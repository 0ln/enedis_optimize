#!/usr/bin/python3

import fileinput, datetime as dt, statistics as st

kWh = {"standard": .174, "low": .147, "high": .1841}
lows = [
    [(2, 7), (12.5, 15.5)],
    [(3, 8), (13.5, 16.5)],
    [(0, 8)],
    [(0, 6.5), (22.5, 24)]
]

print("Enedis Optimize")
print()

data = [i.strip("\n").split(";") for i in fileinput.input() if i[-2:] != ";\n"]
del data[:data.index(["Horodate", "Valeur"]) + 1]
data = [(dt.datetime.fromisoformat(i[0]), int(i[1])) for i in data]

cost = {"standard": {}, "lows": [{},] * len(lows)}
delta_total = dt.timedelta()
for i in enumerate(lows):
    for j in enumerate(data):
        delta = abs(j[1][0] - data[j[0] - (1 if j[0] > 0 else -1)][0])
        if delta > dt.timedelta(hours = 1):
            delta_total -= delta
            delta = abs(j[1][0] - data[j[0] - (1 if j[0] == len(data) - 1 else -1)][0])
            delta_total += delta
        cost["standard"][j[1][0]] = j[1][1] * kWh["standard"] / 1000 * delta / dt.timedelta(hours = 1)
        cost["lows"][i[0]][j[1][0]] = j[1][1] * list(kWh.values())[1:][any(k[0] <= (j[1][0] - delta).hour < k[1] for k in i[1])] / 1000 * delta / dt.timedelta(hours = 1)

delta_total = (delta_total + data[-1][0] - data[0][0]) / dt.timedelta(days = 365.2425 / 12)
print("Costs:")
print("\tStandard:", "{0:.02f}".format((monthly_standard := sum(cost["standard"].values())) / delta_total), "monthly")
print("\tLows:")
for i in enumerate(cost["lows"]): print("\t\t" + str(lows[i[0]]) + ":", "{0:.02f}".format(sum(i[1].values()) / delta_total), "monthly")
cost["lows"] = {i[0]: st.fmean([cost["lows"][j][i[0]] for j in range(len(lows))]) for i in data}
print("\t\tAverage:", "{0:.02f}".format((monthly_lows := sum(cost["lows"].values())) / delta_total), "monthly")
print("\tDifference:", "{0:+.02f}".format((monthly_lows - monthly_standard) / delta_total), "monthly")
print()
