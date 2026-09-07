















## TODO ##
# create bar chart with percentages
# - one per region
# - one overall
# - one overall with stomps
# - one overall with total numbers instead of percentages












































import orjson
import matplotlib.pyplot as plt
from VCT_data import data_VCT_new

forces = {"2977": {"name": "Americas", "pw": 0, "pl": 0, "bw": 0, "bl": 0, "aw": 0, "al": 0},
           "2776": {"name": "Pacific", "pw": 0, "pl": 0, "bw": 0, "bl": 0, "aw": 0, "al": 0},
           "2976": {"name": "EMEA", "pw": 0, "pl": 0, "bw": 0, "bl": 0, "aw": 0, "al": 0}}

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
    event = eventTransfer[event]

    roundWins = [r[0] for r in game["roundWins"]]
    teams = game["teams"]
    roundEco = game["roundEcos"]
    key = "p"
    
    for startingIndex in (0, 12):
        if len(roundEco) - startingIndex <= 1: continue
        loserIndex = 0 if roundWins[startingIndex] == teams[1] else 1

        forcedKey = "f" if float(roundEco[startingIndex+1][loserIndex]) < 4.5 else "n"
        results[event][key + forcedKey] += 1

        if forcedKey == "f":
            forceWonKey = "w" if roundWins[startingIndex] != roundWins[startingIndex+1] else "l" # force won!
            forces[event][key + forceWonKey] += 1

    if len(roundEco) < 14: continue
    stompKey = "s" if roundWins[:12].count(roundWins[12]) >= 9 else "c" # if 10-3 or worse
    stomps[event][key + stompKey] += 1


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

        forcedKey = "f" if float(roundEco[startingIndex+1][loserIndex]) < 4.5 else "n"
        results[event][key + forcedKey] += 1

        if forcedKey == "f":
            forceWonKey = "w" if roundWins[startingIndex] != roundWins[startingIndex+1] else "l" # force won!
            forces[event][key + forceWonKey] += 1

    if len(roundEco) < 14: continue
    stompKey = "s" if roundWins[:12].count(roundWins[12]) >= 9 else "c" # if 10-3 or worse
    stomps[event][key + stompKey] += 1
        

overall = {"pw": 0, "pl": 0, "bw": 0, "bl": 0, "aw": 0, "al": 0, "pf": 0, "pn": 0, "bf": 0, "bn": 0, "af": 0, "an": 0, "ps": 0, "pc": 0, "bs": 0, "bc": 0, "as": 0, "ac": 0}
for event, values in results.items():
    stomp = stomps[event]
    force = forces[event]
    combined = values | stomp | force
    for key in combined:
        if key == "name": continue
        overall[key] += combined[key]

    print("Region: " + values["name"])
    print(f"Non forced rounds in stage 1: {combined["pn"]}")
    print(f"Forced rounds in stage 1: {combined["pf"]}")
    print(f"Non forced rounds in stage 2 groups: {combined["bn"]}")
    print(f"Forced rounds in stage 2 groups: {combined["bf"]}")
    print(f"Non forced rounds in stage 2 groups: {combined["an"]}")
    print(f"Forced rounds in stage 2 groups {combined["af"]}")
    print("-------------------------------")

    print(f"Forced rounds won in stage 1: {combined["pw"]}")
    print(f"Forced rounds lost in stage 1: {combined["pl"]}")
    print(f"Forced rounds won in stage 2 groups: {combined["bw"]}")
    print(f"Forced rounds lost in stage 2 groups: {combined["bl"]}")
    print(f"Forced rounds won in stage 2 play-ins + playoffs: {combined["aw"]}")
    print(f"Forced rounds lost in stage 2 play-ins + playoffs: {combined["al"]}")
    print("-------------------------------")

    print(f"Non stomp games in stage 1: {combined["pc"]}")
    print(f"Stomp games in stage 1: {combined["ps"]}")
    print(f"Non stomp games in stage 2 groups: {combined["bc"]}")
    print(f"Stomp games in stage 2 groups: {combined["bs"]}")
    print(f"Non stomp games in stage 2 play-ins + playoffs: {combined["ac"]}")
    print(f"Stomp games in stage 2 play-ins + playoffs: {combined["as"]}")
    print("-------------------------------")

    print(f"Stage 1 stomp rate: {combined["ps"]/(combined["ps"]+combined["pc"])*100:.2f}%")
    print(f"Stage 1 force rate: {combined["pf"]/(combined["pf"]+combined["pn"])*100:.2f}%")
    print(f"Stage 1 force round win rate: {combined["pw"]/(combined["pw"]+combined["pl"])*100:.2f}%")
    print(f"Stage 2 before stomp rate: {combined["bs"]/(combined["bs"]+combined["bc"])*100:.2f}%")
    print(f"Stage 2 before force rate: {combined["bf"]/(combined["bf"]+combined["bn"])*100:.2f}%")
    print(f"Stage 2 before force round win rate: {combined["bw"]/(combined["bw"]+combined["bl"])*100:.2f}%")
    print(f"Stage 2 after stomp rate: {combined["as"]/(combined["as"]+combined["ac"])*100:.2f}%")
    print(f"Stage 2 after force rate: {combined["af"]/(combined["af"]+combined["an"])*100:.2f}%")
    print(f"Stage 2 after force round win rate: {combined["aw"]/(combined["aw"]+combined["al"])*100:.2f}%")
    print("-------------------------------")
    print("-------------------------------")

print("Overall stats:")
print(f"Non forced rounds in stage 1: {overall["pn"]}")
print(f"Forced rounds in stage 1: {overall["pf"]}")
print(f"Non forced rounds in stage 2 groups: {overall["bn"]}")
print(f"Forced rounds in stage 2 groups: {overall["bf"]}")
print(f"Non forced rounds in stage 2 play-ins + playoffs: {overall["an"]}")
print(f"Forced rounds in stage 2 play-ins + playoffs: {overall["af"]}")
print("-------------------------------")

print(f"Forced rounds won in stage 1: {overall["pw"]}")
print(f"Forced rounds lost in stage 1: {overall["pl"]}")
print(f"Forced rounds won in stage 2 groups: {overall["bw"]}")
print(f"Forced rounds lost in stage 2 groups: {overall["bl"]}")
print(f"Forced rounds won in stage 2 play-ins + playoffs: {overall["aw"]}")
print(f"Forced rounds lost in stage 2 play-ins + playoffs: {overall["al"]}")
print("-------------------------------")

print(f"Non stomp games in stage 1: {overall["pc"]}")
print(f"Stomp games in stage 1: {overall["ps"]}")
print(f"Non stomp games in stage 2 groups: {overall["bc"]}")
print(f"Stomp games in stage 2 groups: {overall["bs"]}")
print(f"Non stomp games in stage 2 play-ins + playoffs: {overall["ac"]}")
print(f"Stomp games in stage 2 play-ins + playoffs: {overall["as"]}")
print("-------------------------------")

print(f"Stage 1 stomp rate: {overall["ps"]/(overall["ps"]+overall["pc"])*100:.2f}%")
print(f"Stage 1 force rate: {overall["pf"]/(overall["pf"]+overall["pn"])*100:.2f}%")
print(f"Stage 1 force round win rate: {overall["pw"]/(overall["pw"]+overall["pl"])*100:.2f}%")
print(f"Stage 2 before stomp rate: {overall["bs"]/(overall["bs"]+overall["bc"])*100:.2f}%")
print(f"Stage 2 before force rate: {overall["bf"]/(overall["bf"]+overall["bn"])*100:.2f}%")
print(f"Stage 2 before force round win rate: {overall["bw"]/(overall["bw"]+overall["bl"])*100:.2f}%")
print(f"Stage 2 after stomp rate: {overall["as"]/(overall["as"]+overall["ac"])*100:.2f}%")
print(f"Stage 2 after force rate: {overall["af"]/(overall["af"]+overall["an"])*100:.2f}%")
print(f"Stage 2 after force round win rate: {overall["aw"]/(overall["aw"]+overall["al"])*100:.2f}%")

data = forces["2976"] | results["2976"] | stomps["2976"]

fig, ax = plt.subplots(figsize=(8, 6))
res = ax.grouped_bar({"Force Rate": [data["pf"]/(data["pf"]+data["pn"])*100,
                                     data["bf"]/(data["bf"]+data["bn"])*100,
                                     data["af"]/(data["af"]+data["an"])*100],
                      "Force Round Win Rate": [data["pw"]/(data["pw"]+data["pl"])*100,
                                               data["bw"]/(data["bw"]+data["bl"])*100,
                                               data["aw"]/(data["aw"]+data["al"])*100],
                      "Stomp Rate": [data["ps"]/(data["ps"]+data["pc"])*100,
                                     data["bs"]/(data["bs"]+data["bc"])*100,
                                     data["as"]/(data["as"]+data["ac"])*100]},
                     tick_labels=("Stage 1", "Stage 2 pre-video", "Stage 2 post-video"),
                     group_spacing=1)

ax.set_title("VCT 2026 Stage 1 & 2 EMEA Forcing Data")
ax.set_ylim(0, 75)
for container in res.bar_containers:
    ax.bar_label(container, padding=3, fmt="{:.2f}%")
ax.legend(loc='upper left')
plt.tight_layout()

plt.show()

