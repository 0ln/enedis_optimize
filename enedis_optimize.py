#!/usr/bin/python3

__version__ = "1.1.0"

import fileinput, sys, signal as si, datetime as dt, base64 as b64, statistics as st, colorama as co, json, requests

co.init(autoreset = True)
print(co.Style.BRIGHT + co.Fore.MAGENTA + "\nEnedis Optimize\n")

def handle_sigint(*_):
    print(co.Style.DIM + "\nAborting...\n")
    co.deinit()
    sys.exit(1)

si.signal(si.SIGINT, handle_sigint)

print(co.Style.DIM + "Loading configuration...")
try: config = json.load(open("config.json"))
except FileNotFoundError:
    print(co.Style.DIM + "No configuration found, please create one using the sample.\n")
    co.deinit()
    sys.exit(1)
for i in enumerate(config):
    try: config[i[0]]["lows"] = [[tuple(map(lambda x: dt.time.max if int(x.split(":")[0]) > 23 else dt.time.fromisoformat(x), k)) for k in j] for j in i[1]["lows"]]
    except KeyError: pass

def parse_enedis(csv = fileinput.input()):
    print(co.Style.DIM + "Parsing Enedis data...")
    data = [i.strip("\n").split(";") for i in csv if i[-2:] != ";\n"]
    del data[:data.index(["Horodate", "Valeur"]) + 1]
    return [(dt.datetime.fromisoformat(i[0]), int(i[1])) for i in data]

def get_delta(data):
    for i in enumerate(data):
        try:
            delta = abs(i[1][0] - data[i[0] - (1 if i[0] > 0 else -1)][0])
            if delta > dt.timedelta(hours = 1): delta = abs((data[i[0] - 1][0] if i[0] == len(data) else i[1][0]) - data[i[0] - (2 if i[0] == len(data) - 1 else -1)][0])
        except IndexError: delta = dt.timedelta(minutes = data[0][0].minute) or dt.timedelta(hours = 1)
        if len(i[1]) < 3: data[i[0]] += (delta,)
    return data

def filter_config(mode = "api"): return list(filter(lambda x: x[1]["mode"] == mode, enumerate(config)))

def retrieve_rte(data, timezones, config = filter_config()):
    rates = {i[0]: [] for i in config}
    for i in config:
        access_token = requests.post(i[1]["api"]["url_auth"], headers = {"Authorization": "Basic " + b64.b64encode(bytes(i[1]["api"]["client"] + ":" + i[1]["api"]["secret"], "utf-8")).decode("utf-8")}).json()["access_token"]
        for j in i[1]["lows"]:
            start_time = j[0][1]
            end_date = dt.datetime.combine(data[-1][0].date() + dt.timedelta(days = 1), dt.time.min, dt.timezone(min(timezones)))
            start_date = min((end_date - dt.timedelta(days = 2)).replace(tzinfo = dt.timezone(max(timezones))), dt.datetime.combine(data[0][0].date() - dt.timedelta(days = 1), dt.time.min, dt.timezone(max(timezones))))
            rates[i[0]].append(requests.get(i[1]["api"]["url_data"], headers = {"Authorization": "Bearer " + access_token}, params = {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}).json()["tempo_like_calendars"]["values"])
            for k in enumerate(rates[i[0]][-1]):
                entry = lambda x: dt.datetime.fromisoformat(k[1][x])
                rates[i[0]][-1][k[0]] |= {l: (lambda x: dt.datetime.combine(x.date(), start_time, x.tzinfo))(entry(l)) for l in ("start_date", "end_date")} | {l: entry(l) for l in ("updated_date",)}
    for i in enumerate(data):
        if len(i[1]) < 4:
            data[i[0]] += ({j[0]: [] for j in config},)
            for k, v in rates.items():
                for j in v:
                    for l in j:
                        if l["start_date"] <= i[1][0] < l["end_date"]:
                            data[i[0]][-1][k].append(l["value"])
                            break
    return data

def get_monthly_data(data = parse_enedis()):
    print(co.Style.DIM + "Calling RTE API and sorting data...")
    return (lambda x: {j: retrieve_rte(get_delta([k for k in data if k[0].date().replace(day = 1) == j]), x) for j in sorted({dt.date(i[0].year, i[0].month, 1) for i in data})})({i[0].utcoffset() for i in data})

def log(indent = 0, *args): print("\t" * indent + " ".join(args))

def log_entry(left, right, title = co.Fore.MAGENTA + "Average", indent = 1):
    diff = right - left
    color = co.Fore.RED if diff > 0 else co.Fore.GREEN if diff < 0 else co.Fore.YELLOW
    log(indent, co.Style.BRIGHT + title + co.Style.RESET_ALL + ":", f"{left:.02f}", "→", f"{right:.02f}", f"({color}{diff:+.02f}{co.Fore.RESET})")

def get_diff(config = (0, config[0]), base = None, data = get_monthly_data()):
    data = data.copy()
    if base != None: log(0, co.Style.BRIGHT + co.Fore.CYAN + config[1]["name"])
    match config[1]["mode"]:
        case "unique": price = lambda _: config[1]["kWh"]
        case "lows": price = lambda x: st.fmean([config[1]["kWh"][not any([j[0] <= x[0].time() < j[1] for j in i])] for i in config[1]["lows"]])
        case "api": price = lambda x: st.fmean([config[1]["kWh"][x[3][config[0]][i[0]]][not any([j[0] <= x[0].time() < j[1] for j in i[1]])] for i in enumerate(config[1]["lows"])])
    for k, v in data.items():
        data[k] = sum([i[1] * (i[2] / dt.timedelta(hours = 1)) / 1000 * price(i) for i in v]) / (sum([i[2] for i in v], dt.timedelta()) / dt.timedelta(days = 1)) * (k.replace(month = k.month % 12 + 1) - dt.timedelta(days = 1)).day + config[1]["monthly"]
        if base != None: log_entry(base[k], data[k], k.strftime("%Y-%m") + co.Style.RESET_ALL)
    if base != None:
        log_entry(*[st.fmean(i.values()) for i in (base, data)])
    else: return data

print()
base = get_diff()
for i in enumerate(config[1:], 1):
    get_diff(i, base)
    print()

co.deinit()
