import orjson
import matplotlib.pyplot as plt

with open("VCT_data/data_VCT.json") as file:
    data = orjson.loads(file.read())

scorelines = {}
for game in data:
    roundWins = [r[0] for r in game["roundWins"]]
    gameWinner = roundWins[-1]
    winnerWins = roundWins[:12].count(gameWinner)
    loserWins = 12 - winnerWins
    saved_winnerWins = winnerWins
    saved_loserWins = loserWins
    for i in range(12, min(len(roundWins)-1, 24)):
        if roundWins[i] == gameWinner:
            winnerWins += 1
        else:
            loserWins += 1
        if winnerWins == loserWins:
            continue
        elif winnerWins >= loserWins:
            scoreline = (loserWins, winnerWins)
        else:
            scoreline = (winnerWins, loserWins)

        if (loserWins, winnerWins) not in scorelines:
            scorelines[(loserWins, winnerWins)] = [0, 0]
        if (winnerWins, loserWins) not in scorelines:
            scorelines[(winnerWins, loserWins)] = [0, 0]
        if loserWins != winnerWins:
            scorelines[(loserWins, winnerWins)][1] += 1
        scorelines[(winnerWins, loserWins)][1] += 1
        scorelines[(winnerWins, loserWins)][0] += 1
    if max(winnerWins, loserWins) >= 14:
        print(game["matchID"], roundWins, winnerWins, loserWins, saved_winnerWins, saved_loserWins)


sorted_scorelines = sorted([[scoreline, percent[0]/percent[1]] for scoreline, percent in scorelines.items()], key=lambda x: x[1])

#for scoreline in sorted_scorelines:
#    print(f"{scoreline[0]}: {scoreline[1]*100:.2f}%")

fig, ax = plt.subplots(figsize=(18, 8))

x = [str(s[0]) for s in sorted_scorelines]
y = [s[1]*100 for s in sorted_scorelines]

ax.bar(x, y)
ax.set_xlabel("Scoreline")
ax.set_ylabel("Chance of winning the game")
ax.set_title("Chance of winning a game from certain scorelines")

ax.set_yticks(list(range(0, 101, 10)))
ax.grid(axis="y")
ax.tick_params("x", rotation=45, rotation_mode="xtick")
plt.tight_layout()
plt.show()

