#!/usr/bin/python3

import fileinput, datetime

data = [i.strip("\n").split(";") for i in fileinput.input()]
del data[:data.index(["Horodate", "Valeur"]) + 1]
data = [(datetime.fromisoformat(i[0]), int(i[1])) for i in data]
