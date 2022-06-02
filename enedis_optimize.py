#!/usr/bin/python3

__version__ = "1.0.0"

from ast import match_case
import fileinput, sys, datetime as dt, base64 as b64, statistics as st, json, requests

print("Enedis Optimize")
print()

try: config = json.load(open("config.json"))
except FileNotFoundError:
    print("No configuration found, please create one using the sample.")
    sys.exit(1)
for i in enumerate(config):
    try: config[i[0]]["lows"] = [[tuple(map(lambda x: dt.time.fromisoformat(k) if k == "24:00" else dt.time.max, k)) for k in j] for j in i[1]["lows"]]
    except KeyError: pass

def parse_enedis(csv = fileinput.input()):
    data = [i.strip("\n").split(";") for i in csv if i[-2:] != ";\n"]
    del data[:data.index(["Horodate", "Valeur"]) + 1]
    return [(dt.datetime.fromisoformat(i[0]), int(i[1])) for i in data]

def get_delta(data):
    data = [i[:2] for i in data]
    for i in enumerate(data):
        try:
            delta = abs(i[1][0] - data[i[0] - (1 if i[0] > 0 else -1)][0])
            if delta > dt.timedelta(hours = 1): delta = abs((data[i[0] - 1][0] if i[0] == len(data) else i[1][0]) - data[i[0] - (2 if i[0] == len(data) - 1 else -1)][0])
        except IndexError: delta = dt.timedelta(minutes = data[0][0].minute) or dt.timedelta(hours = 1)
        if len(i[1]) < 3: data[i[0]] += (delta,)
        return data

def filter_config(mode = "api"): return [i for i in enumerate(config) if i[1]["mode"] == mode]

def retrieve_rte(data, config = filter_config()):
    rates = {i[0]: [] for i in config}
    for i in config:
        access_token = requests.post(config[i[0]]["url_auth"], headers = {"Authorization": "Basic " + b64.b64encode(bytes(config[i[0]]["username"] + ":" + config[i[0]]["password"], "utf-8")).decode("utf-8")}).json()["access_token"]
        for j in i[1]["lows"]:
            start_time = j[0][1]
            end_date = data[-1][0] - data[-1][0].time() + dt.timedelta(days = 1)
            start_date = min(end_date - dt.timedelta(days = 2), data[0][0] - data[0][0].time() - dt.timedelta(days = 1))
            rates[i[0]].append(requests.get(config[i[0]]["url_data"], headers = {"Authorization": "Bearer " + access_token}, params = {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}).json()["tempo_like_calendars"]["values"])
            for k in enumerate(rates[i[0]][-1]):
                entry = lambda l: dt.datetime.fromisoformat(k[1][l])
                rates[i[0]][-1][k[0]] |= {l: entry(l) if l == "updated_date" else dt.datetime.combine(entry(l).date(), start_time, entry(l).tzinfo) for l in ("start_date", "end_date", "updated_date")}
    for i in enumerate(data):
        if len(i[1]) < 4:
            data[i[0]] += ({},)
            for k, v in rates:
                for j in v:
                    if j["start_date"] <= i[1][0] < j["end_date"]:
                        data[i[0]][3][k] = j["value"]
                        break
    return data

def get_monthly_data(data = parse_enedis()): return {j: retrieve_rte(get_delta([k for k in data if k[0].date().replace(day = 1) == j])) for j in sorted(set([dt.date(i[0].year, i[0].month, 1) for i in data]))}

def log(indent = 0, *args): print("\t" * indent, *args)

def log_entry(left, right, title = "Average", indent = 1): log(indent, title + ":", f"{left:.02f}", "→", f"{right:.02f}", f"({right - left:+.02f})")

monthly_data = get_monthly_data()

def get_diff(config = enumerate(config)[0], base = None, data = monthly_data):
    if base != None: log(0, config[1]["name"])
    match config[1]["mode"]:
        case "unique": price = lambda x: config[1]["kWh"]
        case "lows": price = lambda x: st.fmean([config[1]["kWh"][not any([j[0] <= x[0].time() < j[1] for j in i])] for i in config[1]["lows"]])
        case "api": price = lambda x: st.fmean([config[1]["kWh"][x[3][config[0]]][not any([j[0] <= x[0].time() < j[1] for j in i])] for i in config[1]["lows"]])
    for k, v in data:
        data[k] = sum([i[1] * (i[2] / dt.timedelta(hours = 1)) * price(i) for i in v[0]]) / (sum([i[2] for i in v[0]]) / dt.timedelta(days = 1)) * (k.replace(month = k.month % 12 + 1) - dt.timedelta(days = 1)).day + config[1]["monthly"]
        if base != None: log_entry(base[k], data[k], k.strftime("%Y-%m"))
    if base != None: log_entry(*[st.fmean(i.values()) for i in (base, data)])
    return data

base = get_diff()
for i in enumerate(config)[1:]: get_diff(i, base)
