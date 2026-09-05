import matplotlib.pyplot as plt
from VCT_data import data_VCT_new

data = data_VCT_new.data

results = {"2977": {"bf": 0, "af": 0, "bn": 0, "an": 0},
           "2776": {"bf": 0, "af": 0, "bn": 0, "an": 0},
           "2976": {"bf": 0, "af": 0, "bn": 0, "an": 0}
           }

for game in data:
    event = game["eventID"]

    roundWins = [r[0] for r in game["roundWins"]]
    teams = game["teams"]
    roundEco = game["roundEcos"]
    
    for startingIndex in (0, 12):
        if len(roundEco) - startingIndex <= 1: continue
        loserIndex = 0 if roundWins[startingIndex] == teams[1] else 1

        key = "b" if game["month"] == "July" or (game["month"] == "August" and int(game["day"]) <= 11) else "a"
        key += "f" if float(roundEco[startingIndex+1][loserIndex]) < 4.5 else "n"

        results[event][key] += 1
        

for event, values in results.items():
    print(f"eventID: {event}")
    print(f"non forced rounds before: {values["bn"]}")
    print(f"forced rounds before: {values["bf"]}")
    print(f"non forced rounds after: {values["an"]}")
    print(f"forced rounds after: {values["af"]}")
    print(f"Before force rate: {values["bf"]/(values["bf"]+values["bn"])*100:.2f}%")
    print(f"After force rate: {values["af"]/(values["af"]+values["an"])*100:.2f}%")
    print("-------------------------------")
