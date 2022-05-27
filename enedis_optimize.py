#!/usr/bin/python3

import fileinput, datetime as dt, statistics as st, json

config = json.load(open("config.json"))

print("Enedis Optimize")
print()

data = [i.strip("\n").split(";") for i in fileinput.input() if i[-2:] != ";\n"]
del data[:data.index(["Horodate", "Valeur"]) + 1]
data = [(dt.datetime.fromisoformat(i[0]), int(i[1])) for i in data]

def get_diff(data = data, month = None):
    cost = {"standard": {}, "lows": [{},] * len(config["lows"])}
    delta_total = dt.timedelta()
    for i in enumerate(config["lows"]):
        for j in enumerate(data):
            try:
                delta = abs(j[1][0] - data[j[0] - (1 if j[0] > 0 else -1)][0])
                if delta > dt.timedelta(hours = 1):
                    delta_total -= delta
                    delta = abs((data[j[0] - 1][0] if j[0] == len(data) else j[1][0]) - data[j[0] - (2 if j[0] == len(data) - 1 else -1)][0])
                    delta_total += delta
            except IndexError: delta_total = delta = dt.timedelta(minutes = data[0][0].minute) or dt.timedelta(hours = 1)
            cost["standard"][j[1][0]] = j[1][1] * config["kWh"]["standard"] / 1000 * delta / dt.timedelta(hours = 1)
            cost["lows"][i[0]][j[1][0]] = j[1][1] * list(config["kWh"].values())[1:][any(k[0] <= (j[1][0] - delta).hour < k[1] for k in i[1])] / 1000 * delta / dt.timedelta(hours = 1)

    delta_total += data[-1][0] - data[0][0]
    if month == None: delta_total /= dt.timedelta(days = 365.2425 / 12)
    else: delta_total /= dt.timedelta(days = (dt.date(month[1], month[0] % 12 + 1, 1) - dt.timedelta(days = 1)).day)
    if month == None:
        print("Costs:")
        print("\tStandard:", "{0:.02f}".format((standard_total := sum(cost["standard"].values())) / delta_total), "monthly")
        print("\tLows:")
        for i in enumerate(cost["lows"]): print("\t\t" + str(config["lows"][i[0]]) + ":", "{0:.02f}".format(sum(i[1].values()) / delta_total), "monthly")
    else: standard_total = sum(cost["standard"].values()) / delta_total
    cost["lows"] = {i[0]: st.fmean([cost["lows"][j][i[0]] for j in range(len(config["lows"]))]) for i in data}
    if month == None:
        print("\t\tAverage:", "{0:.02f}".format((lows_total := sum(cost["lows"].values())) / delta_total), "monthly")
        print("\tDifference:", "{0:+.02f}".format((lows_total - standard_total) / delta_total), "monthly")
        print("\tDetails per month:")
        for i in sorted(set([(j[0].month, j[0].year) for j in data]), key = lambda x: x[1] * 100 + x[0]): get_diff(list(filter(lambda x: (x[0].month, x[0].year) == i, data)), i)
        print()
    else:
        lows_total = sum(cost["lows"].values()) / delta_total
        print("\t\t" + "{0:%b} {0:%Y}".format(dt.date(*reversed(month), 1)) + ":", f"{standard_total:.02f} → {lows_total:.02f}", "(" + "{0:+.02f}".format(lows_total - standard_total) + ")")

get_diff()
