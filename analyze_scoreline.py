import orjson
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

with open("VCT_data/data_VCT.json") as file:
    data = orjson.loads(file.read())

# NORMAL
#scorelines = {}

# FORCING
# manual adjustment rahhhh
not_forced_scorelines = {(1, 12): [0, 1]}
forced_scorelines = {(12, 1): [1, 1]}

for game in data:
    roundWins = [r[0] for r in game["roundWins"]]
    if len(roundWins) == 0: continue

    # FORCING
    if len(roundWins) <= 13: continue
    gameWinner = roundWins[-1]
    secondPistolWinner = roundWins[12]
    sPWinnerWins = roundWins[:12].count(secondPistolWinner)
    sPLoserWins = 12 - sPWinnerWins
    sPWinnerWins += 1
    
    roundEcos = game["roundEcos"]
    teams = game["teams"]
    secondPistolLoserIndex = 1 if teams[0] == secondPistolWinner else 0
    secondPistolLoserForced = roundEcos[13][secondPistolLoserIndex] < 4.5

    scorelines = forced_scorelines if secondPistolLoserForced else not_forced_scorelines

    if sPLoserWins == 8 and scorelines == forced_scorelines:
        print(roundEcos[13][secondPistolLoserIndex])
        print("won" if secondPistolWinner != gameWinner else "lost")

    if (sPLoserWins, sPWinnerWins) not in scorelines:
        scorelines[(sPLoserWins, sPWinnerWins)] = [0, 1]
    else:
        scorelines[(sPLoserWins, sPWinnerWins)][1] += 1

    if secondPistolWinner != gameWinner:
        scorelines[(sPLoserWins, sPWinnerWins)][0] += 1


    # NORMAL
    #gameWinner = roundWins[-1]
    #winnerWins = roundWins[:12].count(gameWinner)
    #loserWins = 12 - winnerWins

    #if winnerWins != loserWins:
    #    if (loserWins, winnerWins) not in scorelines:
    #        scorelines[(loserWins, winnerWins)] = [0, 0]
    #    if (winnerWins, loserWins) not in scorelines:
    #        scorelines[(winnerWins, loserWins)] = [0, 0]
    #    scorelines[(loserWins, winnerWins)][1] += 1
    #    scorelines[(winnerWins, loserWins)][1] += 1
    #    scorelines[(winnerWins, loserWins)][0] += 1

    #for i in range(12, min(len(roundWins)-1, 24)):
    #    if roundWins[i] == gameWinner:
    #        winnerWins += 1
    #    else:
    #        loserWins += 1
    #    if winnerWins == loserWins:
    #        continue
    #    elif winnerWins >= loserWins:
    #        scoreline = (loserWins, winnerWins)
    #    else:
    #        scoreline = (winnerWins, loserWins)

    #    if max(winnerWins, loserWins) >= 13:
    #        break
    #    if (loserWins, winnerWins) not in scorelines:
    #        scorelines[(loserWins, winnerWins)] = [0, 0]
    #    if (winnerWins, loserWins) not in scorelines:
    #        scorelines[(winnerWins, loserWins)] = [0, 0]
    #    scorelines[(loserWins, winnerWins)][1] += 1
    #    scorelines[(winnerWins, loserWins)][1] += 1
    #    scorelines[(winnerWins, loserWins)][0] += 1


# FORCING
fig, ax = plt.subplots(figsize=(18, 8))
ax.set_title("VCT 2023-Present Data: Chance of Winning a Map After You Lose 2nd Pistol and Force/Don't Force")
forced_sorted_scorelines = sorted([[scoreline, percent[0]/percent[1]*100] for scoreline, percent in forced_scorelines.items()], key=lambda x: x[0][0])
not_forced_sorted_scorelines = sorted([[scoreline, percent[0]/percent[1]*100] for scoreline, percent in not_forced_scorelines.items()], key=lambda x: x[0][0])

res = ax.grouped_bar({'Forced': [s[1] for s in forced_sorted_scorelines],
                      'Not Forced': [s[1] for s in not_forced_sorted_scorelines]},
                     tick_labels=[s[0] for s in forced_sorted_scorelines], group_spacing=0.5, colors=("mediumblue", "forestgreen"))
for container in res.bar_containers:
    ax.bar_label(container, padding=3, fmt="%.1f%%")

print("forced")
for scoreline in forced_sorted_scorelines:
    print(f"{scoreline[0]}: {scoreline[1]:.2f}%")
print("not_forced")
for scoreline in not_forced_sorted_scorelines:
    print(f"{scoreline[0]}: {scoreline[1]:.2f}%")

#colors = plt.colormaps['RdYlGn'](mcolors.Normalize(vmin=0, vmax=100)(y))

ax.set_xlabel("Scoreline")
ax.set_ylabel("% Chance of Winning the Map")

ax.set_yticks(list(range(0, 101, 10)))
ax.tick_params("x", rotation=45, rotation_mode="xtick")
ax.legend()

plt.tight_layout()
plt.show()

#sorted_scorelines = sorted([[scoreline, percent[0]/percent[1]] for scoreline, percent in scorelines.items()], key=lambda x: x[1] + 0.0001*x[0][0])
#
#for scoreline in sorted_scorelines:
#    print(f"{scoreline[0]}: {scoreline[1]*100:.2f}%")
#
#fig, ax = plt.subplots(figsize=(18, 8))
#
#x = [str(s[0]) for s in sorted_scorelines]
#y = [s[1]*100 for s in sorted_scorelines]
#colors = plt.colormaps['RdYlGn'](mcolors.Normalize(vmin=0, vmax=100)(y))
#
#ax.bar(x, y, color=colors)
#
#ax.set_xlabel("Scoreline")
#ax.set_ylabel("% Chance of Winning the Map")
#ax.set_title("VCT 2023-Present Data: Chance of Winning a Map After You Lose 2nd Pistol and Don't Force and Lose Again")
#
#ax.set_yticks(list(range(0, 101, 10)))
#ax.grid(axis="y")
#ax.tick_params("x", rotation=45, rotation_mode="xtick")
#plt.tight_layout()
#plt.show()
#
