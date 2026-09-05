















## TODO ##
# create bar chart with percentages
# create dot chart with timeline













































import orjson
import matplotlib.pyplot as plt
from VCT_data import data_VCT_new

stomps = {"2977": {"name": "Americas", "ps": 0, "pc": 0, "bs": 0, "bc": 0, "as": 0, "ac": 0},
           "2776": {"name": "Pacific", "ps": 0, "pc": 0, "bs": 0, "bc": 0, "as": 0, "ac": 0},
           "2976": {"name": "EMEA", "ps": 0, "pc": 0, "bs": 0, "bc": 0, "as": 0, "ac": 0}}

results = {"2977": {"name": "Americas", "pf": 0, "pn": 0, "bf": 0, "af": 0, "bn": 0, "an": 0},
           "2776": {"name": "Pacific", "pf": 0, "pn": 0, "bf": 0, "af": 0, "bn": 0, "an": 0},
           "2976": {"name": "EMEA", "pf": 0, "pn": 0, "bf": 0, "af": 0, "bn": 0, "an": 0}}

eventTransfer = {"2860": "2977",
                 "2863": "2976",
                 "2775": "2776"}

with open("VCT_data/data_VCT.json") as file:
    data = orjson.loads(file.read())

for game in data:
    event = game["eventID"]
    if event not in eventTransfer: continue

    roundWins = [r[0] for r in game["roundWins"]]
    teams = game["teams"]
    roundEco = game["roundEcos"]
    
    for startingIndex in (0, 12):
        if len(roundEco) - startingIndex <= 1: continue
        loserIndex = 0 if roundWins[startingIndex] == teams[1] else 1

        key = "pf" if float(roundEco[startingIndex+1][loserIndex]) < 4.5 else "pn"

        results[eventTransfer[event]][key] += 1

    if len(roundEco) < 14: continue
    key = "ps" if roundWins[:12].count(roundWins[12]) >= 9 else "pc" # if 10-3 or worse
    stomps[eventTransfer[event]][key] += 1


data = data_VCT_new.data

for game in data:
    event = game["eventID"]

    roundWins = [r[0] for r in game["roundWins"]]
    teams = game["teams"]
    roundEco = game["roundEcos"]
    key = "b" if game["month"] == "July" or (game["month"] == "August" and int(game["day"]) <= 11) else "a"
    
    for startingIndex in (0, 12):
        if len(roundEco) - startingIndex <= 1: continue
        loserIndex = 0 if roundWins[startingIndex] == teams[1] else 1

        key = key[0] + ("f" if float(roundEco[startingIndex+1][loserIndex]) < 4.5 else "n")

        results[event][key] += 1

    if len(roundEco) < 14: continue
    key = key[0] + ("s" if roundWins[:12].count(roundWins[12]) >= 9 else "c") # if 10-3 or worse
    stomps[event][key] += 1
        

overall = {"pf": 0, "pn": 0, "bf": 0, "bn": 0, "af": 0, "an": 0, "ps": 0, "pc": 0, "bs": 0, "bc": 0, "as": 0, "ac": 0}
for event, values in results.items():
    stomp = stomps[event]
    overall["pf"] += values["pf"]
    overall["pn"] += values["pn"]
    overall["af"] += values["af"]
    overall["an"] += values["an"]
    overall["bf"] += values["bf"]
    overall["bn"] += values["bn"]
    overall["ps"] += stomp["ps"]
    overall["pc"] += stomp["pc"]
    overall["as"] += stomp["as"]
    overall["ac"] += stomp["ac"]
    overall["bs"] += stomp["bs"]
    overall["bc"] += stomp["bc"]

    print("Region: " + values["name"])
    print(f"Non forced rounds in stage 1: {values["pn"]}")
    print(f"Forced rounds in stage 1: {values["pf"]}")
    print(f"Non forced rounds in stage 2 before TMV video: {values["bn"]}")
    print(f"Forced rounds in stage 2 before TMV video: {values["bf"]}")
    print(f"Non forced rounds in stage 2 after TMV video: {values["an"]}")
    print(f"Forced rounds in stage 2 after TMV video: {values["af"]}")
    print(f"Stage 1 stomp rate: {stomp["ps"]/(stomp["ps"]+stomp["pc"])*100:.2f}%")
    print(f"Stage 1 force rate: {values["pf"]/(values["pf"]+values["pn"])*100:.2f}%")
    print(f"Stage 2 before stomp rate: {stomp["bs"]/(stomp["bs"]+stomp["bc"])*100:.2f}%")
    print(f"Stage 2 before force rate: {values["bf"]/(values["bf"]+values["bn"])*100:.2f}%")
    print(f"Stage 2 after stomp rate: {stomp["as"]/(stomp["as"]+stomp["ac"])*100:.2f}%")
    print(f"Stage 2 after force rate: {values["af"]/(values["af"]+values["an"])*100:.2f}%")
    print("-------------------------------")

print("Overall stats:")
print(f"1 stomp rate: {overall["ps"]/(overall["ps"]+overall["pc"])*100:.2f}%")
print(f"Stage 1 force rate: {overall["pf"]/(overall["pf"]+overall["pn"])*100:.2f}%")
print(f"Stage 2 before stomp rate: {overall["bs"]/(overall["bs"]+overall["bc"])*100:.2f}%")
print(f"Stage 2 before force rate: {overall["bf"]/(overall["bf"]+overall["bn"])*100:.2f}%")
print(f"Stage 2 after stomp rate: {overall["as"]/(overall["as"]+overall["ac"])*100:.2f}%")
print(f"Stage 2 after force rate: {overall["af"]/(overall["af"]+overall["an"])*100:.2f}%")
