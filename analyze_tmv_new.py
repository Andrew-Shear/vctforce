import orjson
import matplotlib.pyplot as plt

forces = {"2977": {"name": "Americas", "fw": 0, "fl": 0, "sw": 0, "sl": 0, "tw": 0, "tl": 0},
           "2776": {"name": "Pacific", "fw": 0, "fl": 0, "sw": 0, "sl": 0, "tw": 0, "tl": 0},
           "2976": {"name": "EMEA", "fw": 0, "fl": 0, "sw": 0, "sl": 0, "tw": 0, "tl": 0}}

results = {"2977": {"name": "Americas", "ff": 0, "fn": 0, "sf": 0, "sn": 0, "tf": 0, "tn": 0},
           "2776": {"name": "Pacific", "ff": 0, "fn": 0, "sf": 0, "sn": 0, "tf": 0, "tn": 0},
           "2976": {"name": "EMEA", "ff": 0, "fn": 0, "sf": 0, "sn": 0, "tf": 0, "tn": 0}}

with open("VCT_data/data_VCT.json") as file:
    data = orjson.loads(file.read())

for game in data:
    event = game["eventID"]
    if event not in results:
        continue

    roundWins = [r[0] for r in game["roundWins"]]
    teams = game["teams"]
    roundEco = game["roundEcos"]

    for startingIndex, key in ((0, "f"), (12, "s")):
        if len(roundEco) - startingIndex <= 1: continue
        loserIndex = 0 if roundWins[startingIndex] == teams[1] else 1

        forcedKey = "f" if float(roundEco[startingIndex+1][loserIndex]) < 4.5 else "n"
        results[event][key + forcedKey] += 1
        results[event]["t" + forcedKey] += 1

        if forcedKey == "f":
            forceWonKey = "w" if roundWins[startingIndex] != roundWins[startingIndex+1] else "l"
            forces[event][key + forceWonKey] += 1
            forces[event]["t" + forceWonKey] += 1

overall = {"fw": 0, "fl": 0, "sw": 0, "sl": 0, "tw": 0, "tl": 0, "ff": 0, "fn": 0, "sf": 0, "sn": 0, "tf": 0, "tn": 0}
for event, values in results.items():
    force = forces[event]
    combined = values | force
    for key in combined:
        if key == "name": continue
        overall[key] += combined[key]

    print("Region: " + combined["name"])
    print(f"Non forced rounds in stage 2: {combined["tn"]}")
    print(f"Forced rounds in stage 2: {combined["tf"]}")
    print(f"Non forced 2nd rounds in stage 2: {combined["fn"]}")
    print(f"Forced 2nd rounds in stage 2: {combined["ff"]}")
    print(f"Non forced 14th rounds in stage 2: {combined["sn"]}")
    print(f"Forced 14th rounds in stage 2: {combined["sf"]}")
    print("-------------------------------")

    print(f"Forced rounds won in stage 2: {combined["tw"]}")
    print(f"Forced rounds lost in stage 2: {combined["tl"]}")
    print(f"Forced 2nd rounds won in stage 2: {combined["fw"]}")
    print(f"Forced 2nd rounds lost in stage 2: {combined["fl"]}")
    print(f"Forced 14th rounds won in stage 2: {combined["sw"]}")
    print(f"Forced 14th rounds lost in stage 2: {combined["sl"]}")
    print("-------------------------------")

    print(f"Stage 2 round force rate: {combined["tf"]/(combined["tf"]+combined["tn"])*100:.2f}%")
    print(f"Stage 2 round force round win rate: {combined["tw"]/(combined["tw"]+combined["tl"])*100:.2f}%")
    print(f"Stage 2 2nd round force rate: {combined["ff"]/(combined["ff"]+combined["fn"])*100:.2f}%")
    print(f"Stage 2 2nd round force round win rate: {combined["fw"]/(combined["fw"]+combined["fl"])*100:.2f}%")
    print(f"Stage 2 14th round force rate: {combined["sf"]/(combined["sf"]+combined["sn"])*100:.2f}%")
    print(f"Stage 2 14th round force round win rate: {combined["sw"]/(combined["sw"]+combined["sl"])*100:.2f}%")
    print("-------------------------------")
    print("-------------------------------")

print("Overall stats:")
print(f"Non forced rounds in stage 2: {overall["tn"]}")
print(f"Forced rounds in stage 2: {overall["tf"]}")
print(f"Non forced 2nd rounds in stage 2: {overall["fn"]}")
print(f"Forced 2nd rounds in stage 2: {overall["ff"]}")
print(f"Non forced 14th rounds in stage 2: {overall["sn"]}")
print(f"Forced 14th rounds in stage 2: {overall["sf"]}")
print("-------------------------------")

print(f"Forced rounds won in stage 2: {overall["tw"]}")
print(f"Forced rounds lost in stage 2: {overall["tl"]}")
print(f"Forced 2nd rounds won in stage 2: {overall["fw"]}")
print(f"Forced 2nd rounds lost in stage 2: {overall["fl"]}")
print(f"Forced 14th rounds won in stage 2: {overall["sw"]}")
print(f"Forced 14th rounds lost in stage 2: {overall["sl"]}")
print("-------------------------------")

print(f"Stage 2 round force rate: {overall["tf"]/(overall["tf"]+overall["tn"])*100:.2f}%")
print(f"Stage 2 round force round win rate: {overall["tw"]/(overall["tw"]+overall["tl"])*100:.2f}%")
print(f"Stage 2 2nd round force rate: {overall["ff"]/(overall["ff"]+overall["fn"])*100:.2f}%")
print(f"Stage 2 2nd round force round win rate: {overall["fw"]/(overall["fw"]+overall["fl"])*100:.2f}%")
print(f"Stage 2 14th round force rate: {overall["sf"]/(overall["sf"]+overall["sn"])*100:.2f}%")
print(f"Stage 2 14th round force round win rate: {overall["sw"]/(overall["sw"]+overall["sl"])*100:.2f}%")

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

for data, ax in ((forces["2977"] | results["2977"], ax1),
                 (forces["2776"] | results["2776"], ax2),
                 (forces["2976"] | results["2976"], ax3),
                 (overall, ax4)):  

    res = ax.grouped_bar({"Force Rate": [data["tf"]/(data["tf"]+data["tn"])*100,
                                         data["ff"]/(data["ff"]+data["fn"])*100,
                                         data["sf"]/(data["sf"]+data["sn"])*100],
                          "Force Round Win Rate": [data["tw"]/(data["tw"]+data["tl"])*100,
                                                   data["fw"]/(data["fw"]+data["fl"])*100,
                                                   data["sw"]/(data["sw"]+data["sl"])*100]},
                         tick_labels=("Stage 2 Total", "Stage 2 2nd Rounds", "Stage 2 14th Rounds"),
                         group_spacing=1)

    ax.set_ylim(0, 75)
    if "name" in data:
        ax.set_title(f"VCT 2026 Stage 2 {data["name"]} Forcing Data")
    else:
        ax.set_title("VCT 2026 Stage 2 Overall Forcing Data")

    for container in res.bar_containers:
        ax.bar_label(container, padding=3, fmt="{:.2f}%")
    ax.legend(loc='upper left')

plt.tight_layout()

plt.show()

