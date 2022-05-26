#!/usr/bin/python3

import fileinput

f = [i.strip("\n") for i in fileinput.input()]
del f[:f.index("Horodate;Valeur") + 1]
