import copy
import orjson
import sys

forced_template = [0, [0, 0], [[0, 0], [0, 0]], [[[0, 0], [0, 0]], [[0, 0], [0, 0]]], [[[[0, 0], [0, 0]], [[0, 0], [0, 0]]], [[[0, 0], [0, 0]], [[0, 0], [0, 0]]]]] # [#won, [won, lost], [[wonwon, wonlost], [lostwon, lostlost]], etc.]
not_forced_template = [0, [0, 0], [[0, 0], [0, 0]], [[[0, 0], [0, 0]], [[0, 0], [0, 0]]], [[[[0, 0], [0, 0]], [[0, 0], [0, 0]]], [[[0, 0], [0, 0]], [[0, 0], [0, 0]]]]] # [#won, [won, lost], [[wonwon, wonlost], [lostwon, lostlost]], etc.]
forced_scores_template = [[0, 0], [0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0, 0]] # [[1-1, 0-2], [2-1, 1-2, 0-3], etc.]
not_forced_scores_template = [[0, 0], [0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0, 0]] # [[1-1, 0-2], [2-1, 1-2, 0-3], etc.]
forced_money_template = [[0, 0], [0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0, 0]] # [[1-1, 0-2], [2-1, 1-2, 0-3], etc.]
not_forced_money_template = [[0, 0], [0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0, 0]] # [[1-1, 0-2], [2-1, 1-2, 0-3], etc.]

def analyzeMapData(data, *, args):
    maps = {}
    teamForceSuccessRate = {}

    for game in data:
        mapName = game["map"]
        if mapName not in maps:
            maps[mapName] = {'forced': copy.deepcopy(forced_template),
                 'not_forced': copy.deepcopy(not_forced_template),
                 'forced_scores': copy.deepcopy(forced_scores_template),
                 'not_forced_scores': copy.deepcopy(not_forced_scores_template),
                 'forced_money': copy.deepcopy(forced_money_template),
                 'not_forced_money': copy.deepcopy(not_forced_money_template)}

        forced = maps[mapName]['forced']
        not_forced = maps[mapName]['not_forced']
        forced_scores = maps[mapName]['forced_scores']
        not_forced_scores = maps[mapName]['not_forced_scores']
        forced_money = maps[mapName]['forced_money']
        not_forced_money = maps[mapName]['not_forced_money']

        analyzeGame(game, forced, not_forced, forced_scores, not_forced_scores, forced_money, not_forced_money, teamForceSuccessRate, args=args)

    for mapName in maps:
        if mapName == "Summit":
            print("Skipping Summit - not enough data")
            continue
        if mapName.lower() == "n/a":
            continue
        
        print(f"map: {mapName}")
        forced = maps[mapName]['forced']
        not_forced = maps[mapName]['not_forced']
        forced_scores = maps[mapName]['forced_scores']
        not_forced_scores = maps[mapName]['not_forced_scores']
        forced_money = maps[mapName]['forced_money']
        not_forced_money = maps[mapName]['not_forced_money']

        printResults(forced, not_forced, forced_money, not_forced_money, forced_scores, not_forced_scores, args=args)
        print("\n\n\n\n")

    if "teams" in args:
        printTeamResults(teamForceSuccessRate)




def analyzeOverallData(data, *, args=[]):
    forced = copy.deepcopy(forced_template)
    not_forced = copy.deepcopy(not_forced_template)
    forced_scores = copy.deepcopy(forced_scores_template)
    not_forced_scores = copy.deepcopy(not_forced_scores_template)
    forced_money = copy.deepcopy(forced_money_template)
    not_forced_money = copy.deepcopy(not_forced_money_template)

    teamForceSuccessRate = {}

    for game in data:
        analyzeGame(game, forced, not_forced, forced_scores, not_forced_scores, forced_money, not_forced_money, teamForceSuccessRate, args=args)

    printResults(forced, not_forced, forced_money, not_forced_money, forced_scores, not_forced_scores, args=args)
    if "teams" in args:
        printTeamResults(teamForceSuccessRate)


def analyzeGame(game, forced, not_forced, forced_scores, not_forced_scores, forced_money, not_forced_money, teamForceSuccessRate, *, args):
    teams = game["teams"]
    roundWins = game["roundWins"]
    roundSpent = game["roundSpent"]
    roundEco = game["roundEcos"]

    # HERE
    roundLossesIndex = [1 if r[0] == teams[0] else 0 for r in roundWins]
    halfRange = (0,12)
    if "first" in args:
        halfRange = (0,)
    elif "second" in args:
        halfRange = (12,)
    for startingIndex in halfRange:
        if len(roundWins) - startingIndex < 2: # not enough rounds in the half to analyze
            break

        loserIndex = roundLossesIndex[startingIndex]
        moneySaved2nd = float(roundEco[startingIndex+1][loserIndex])

        
        # are you on attack or defense?
        if "attack" in args and roundWins[0][1] == 'ct' or "defense" in args and roundWins[0][1] == 't':
            # if the winner of the first round was on attack, then the loser (forcer) was on defense
            continue
        
        current = forced if moneySaved2nd < 4.5 else not_forced # 4.5k
        current_scores = forced_scores if moneySaved2nd < 4.5 else not_forced_scores # 4.5k
        current_money = forced_money if moneySaved2nd < 4.5 else not_forced_money # 4.5k
        current[0] += 1

        # 0 if you won, 1 if you lost
        won2nd = int(roundWins[startingIndex+1] == roundWins[startingIndex])
        current[1][won2nd] += 1
        current_scores[0][won2nd] += 1
        current_money[0][won2nd] += float(roundEco[startingIndex+1][loserIndex])

        # specific team data
        if "teams" in args:
            if current == forced:
                if teams[loserIndex] in teamForceSuccessRate:
                    teamForceSuccessRate[teams[loserIndex]][1] += 1
                else:
                    teamForceSuccessRate[teams[loserIndex]] = [0, 1]
                if won2nd == 0: # if you won the force
                    teamForceSuccessRate[teams[loserIndex]][0] += 1


        if len(roundWins) - startingIndex < 3:
            break
        won3rd = int(roundWins[startingIndex+2] == roundWins[startingIndex])
        current[2][won2nd][won3rd] += 1
        current_scores[1][won2nd + won3rd] += 1
        current_money[1][won2nd + won3rd] += float(roundEco[startingIndex+2][loserIndex])

        if len(roundWins) - startingIndex < 4:
            break
        won4th = int(roundWins[startingIndex+3] == roundWins[startingIndex])
        current[3][won2nd][won3rd][won4th] += 1
        current_scores[2][won2nd + won3rd + won4th] += 1
        current_money[2][won2nd + won3rd + won4th] += float(roundEco[startingIndex+3][loserIndex])
        
        if len(roundWins) - startingIndex < 5:
            break
        won5th = int(roundWins[startingIndex+4] == roundWins[startingIndex])
        current[4][won2nd][won3rd][won4th][won5th] += 1
        current_scores[3][won2nd + won3rd + won4th + won5th] += 1
        current_money[3][won2nd + won3rd + won4th + won5th] += float(roundEco[startingIndex+4][loserIndex])

            # HERE


def printResults(forced, not_forced, forced_money, not_forced_money, forced_scores, not_forced_scores, *, args):
    forced_percent = forced[0]/(forced[0]+not_forced[0])

    forced_won = forced[1][0]/sum(forced[1])
    forced_lost = 1-forced_won

    not_forced_won = not_forced[1][0]/sum(not_forced[1])
    not_forced_lost = 1-not_forced_won

    forced_won_won = forced[2][0][0]/sum(forced[2][0])
    forced_won_lost = 1-forced_won_won
    forced_lost_won = forced[2][1][0]/sum(forced[2][1])
    forced_lost_lost = 1-forced_lost_won

    not_forced_won_won = not_forced[2][0][0]/sum(not_forced[2][0])
    not_forced_won_lost = 1-not_forced_won_won
    not_forced_lost_won = not_forced[2][1][0]/sum(not_forced[2][1])
    not_forced_lost_lost = 1-not_forced_lost_won 

    print(f"number of 2nd rounds analyzed: {forced[0] + not_forced[0]}")
    print(f"number of 2nd rounds forced: {forced[0]}")
    print(f"percentage of 2nd rounds forced: {forced_percent*100:.2f}%")
    print("--------------------------------")
    print(f"percentage of forced 2nd rounds won: {forced_won*100:.2f}%")
    print(f"percentage of forced 2nd rounds lost: {forced_lost*100:.2f}%")
    print(f"percentage of 3rd rounds won after forcing and winning: {forced_won_won*100:.2f}%")
    print(f"percentage of 3rd rounds won after forcing and losing: {forced_lost_won*100:.2f}%")
    print("--------------------------------")
    print(f"percentage of non forced 2nd rounds won: {not_forced_won*100:.2f}%")
    print(f"percentage of non forced 2nd rounds lost: {not_forced_lost*100:.2f}%")
    print(f"percentage of 3rd rounds won after not forcing and winning: {not_forced_won_won*100:.2f}%")
    print(f"percentage of 3rd rounds won after not forcing and losing: {not_forced_lost_won*100:.2f}%")
    print("--------------------------------")
    print("--------------------------------")
    print(f"chance of going 2-1 if you force: {(forced_won*forced_won_won)*100:.2f}%")
    print(f"chance of going 1-2 if you force: {(forced_won*forced_won_lost + forced_lost*forced_lost_won)*100:.2f}%")
    print(f"chance of going 0-3 if you force: {forced_lost*forced_lost_lost*100:.2f}%")
    print("--------------------------------")
    print(f"chance of going 2-1 if you don't force: {(not_forced_won*not_forced_won_won)*100:.2f}%")
    print(f"chance of going 1-2 if you don't force: {(not_forced_won*not_forced_won_lost + not_forced_lost*not_forced_lost_won)*100:.2f}%")
    print(f"chance of going 0-3 if you don't force: {not_forced_lost*not_forced_lost_lost*100:.2f}%")
    print("--------------------------------")
    if "money" in args:
        print(f"average money after going 2-1 if you force: {forced_money[1][0]/forced_scores[1][0]:.1f}k")
        print(f"average money after going 1-2 if you force: {forced_money[1][1]/forced_scores[1][1]:.1f}k")
        print(f"average money after going 0-3 if you force: {forced_money[1][2]/forced_scores[1][2]:.1f}k")
        print("--------------------------------")
        print(f"average money after going 2-1 if you don't force: {not_forced_money[1][0]/not_forced_scores[1][0]:.1f}k")
        print(f"average money after going 1-2 if you don't force: {not_forced_money[1][1]/not_forced_scores[1][1]:.1f}k")
        print(f"average money after going 0-3 if you don't force: {not_forced_money[1][2]/not_forced_scores[1][2]:.1f}k")
        print("--------------------------------")

    if "round4" not in args and "round5" not in args: return

    forced_won_won_won = forced[3][0][0][0]/sum(forced[3][0][0])
    forced_won_won_lost = 1-forced_won_won_won
    forced_won_lost_won = forced[3][0][1][0]/sum(forced[3][0][1])
    forced_won_lost_lost = 1-forced_won_lost_won
    forced_lost_won_won = forced[3][1][0][0]/sum(forced[3][1][0])
    forced_lost_won_lost = 1-forced_lost_won_won
    forced_lost_lost_won = forced[3][1][1][0]/sum(forced[3][1][1])
    forced_lost_lost_lost = 1-forced_lost_lost_won

    not_forced_won_won_won = not_forced[3][0][0][0]/sum(not_forced[3][0][0])
    not_forced_won_won_lost = 1-not_forced_won_won_won
    not_forced_won_lost_won = not_forced[3][0][1][0]/sum(not_forced[3][1][0])
    not_forced_won_lost_lost = 1-not_forced_won_lost_won
    not_forced_lost_won_won = not_forced[3][1][0][0]/sum(not_forced[3][1][0])
    not_forced_lost_won_lost = 1-not_forced_lost_won_won
    not_forced_lost_lost_won = not_forced[3][1][1][0]/sum(not_forced[3][1][1])
    not_forced_lost_lost_lost = 1-not_forced_lost_lost_won

    forced_chance_3_1 = forced_won*forced_won_won*forced_won_won_won
    forced_chance_2_2 = forced_won*forced_won_won*forced_won_won_lost + forced_won*forced_won_lost*forced_won_lost_won + forced_lost*forced_lost_won*forced_lost_won_won
    forced_chance_1_3 = forced_won*forced_won_lost*forced_won_lost_lost + forced_lost*forced_lost_won*forced_lost_won_lost + forced_lost*forced_lost_lost*forced_lost_lost_won
    forced_chance_0_4 = forced_lost*forced_lost_lost*forced_lost_lost_lost

    not_forced_chance_3_1 = not_forced_won*not_forced_won_won*not_forced_won_won_won
    not_forced_chance_2_2 = not_forced_won*not_forced_won_won*not_forced_won_won_lost + not_forced_won*not_forced_won_lost*not_forced_won_lost_won + not_forced_lost*not_forced_lost_won*not_forced_lost_won_won
    not_forced_chance_1_3 = not_forced_won*not_forced_won_lost*not_forced_won_lost_lost + not_forced_lost*not_forced_lost_won*not_forced_lost_won_lost + not_forced_lost*not_forced_lost_lost*not_forced_lost_lost_won
    not_forced_chance_0_4 = not_forced_lost*not_forced_lost_lost*not_forced_lost_lost_lost


    print("--------------------------------")
    print(f"chance of going 3-1 if you force: {forced_chance_3_1*100:.2f}%")
    print(f"chance of going 2-2 if you force: {forced_chance_2_2*100:.2f}%")
    print(f"chance of going 1-3 if you force: {forced_chance_1_3*100:.2f}%")
    print(f"chance of going 0-4 if you force: {forced_chance_0_4*100:.2f}%")
    print("--------------------------------")
    print(f"chance of going 3-1 if you don't force: {not_forced_chance_3_1*100:.2f}%")
    print(f"chance of going 2-2 if you don't force: {not_forced_chance_2_2*100:.2f}%")
    print(f"chance of going 1-3 if you don't force: {not_forced_chance_1_3*100:.2f}%")
    print(f"chance of going 0-4 if you don't force: {not_forced_chance_0_4*100:.2f}%")
    print("--------------------------------")
    if "money" in args:
        print(f"average money after going 3-1 if you force: {forced_money[2][0]/forced_scores[2][0]:.1f}k")
        print(f"average money after going 2-2 if you force: {forced_money[2][1]/forced_scores[2][1]:.1f}k")
        print(f"average money after going 1-3 if you force: {forced_money[2][2]/forced_scores[2][2]:.1f}k")
        print(f"average money after going 0-4 if you force: {forced_money[2][3]/forced_scores[2][3]:.1f}k")
        print("--------------------------------")
        print(f"average money after going 3-1 if you don't force: {not_forced_money[2][0]/not_forced_scores[2][0]:.1f}k")
        print(f"average money after going 2-2 if you don't force: {not_forced_money[2][1]/not_forced_scores[2][1]:.1f}k")
        print(f"average money after going 1-3 if you don't force: {not_forced_money[2][2]/not_forced_scores[2][2]:.1f}k")
        print(f"average money after going 0-4 if you don't force: {not_forced_money[2][3]/not_forced_scores[2][3]:.1f}k")
        print("--------------------------------")

    if "round5" not in args: return

    forced_won_won_won_won = forced[4][0][0][0][0]/sum(forced[4][0][0][0])
    forced_won_won_won_lost = 1-forced_won_won_won_won
    forced_won_won_lost_won = forced[4][0][0][1][0]/sum(forced[4][0][0][1])
    forced_won_won_lost_lost = 1-forced_won_won_lost_won
    forced_won_lost_won_won = forced[4][0][1][0][0]/sum(forced[4][0][1][0])
    forced_won_lost_won_lost = 1-forced_won_lost_won_won
    forced_won_lost_lost_won = forced[4][0][1][1][0]/sum(forced[4][0][1][1])
    forced_won_lost_lost_lost = 1-forced_won_lost_lost_won
    forced_lost_won_won_won = forced[4][1][0][0][0]/sum(forced[4][1][0][0])
    forced_lost_won_won_lost = 1-forced_won_won_won_won
    forced_lost_won_lost_won = forced[4][1][0][1][0]/sum(forced[4][1][0][1])
    forced_lost_won_lost_lost = 1-forced_lost_won_lost_won
    forced_lost_lost_won_won = forced[4][1][1][0][0]/sum(forced[4][1][1][0])
    forced_lost_lost_won_lost = 1-forced_lost_lost_won_won
    forced_lost_lost_lost_won = forced[4][1][1][1][0]/sum(forced[4][1][1][1])
    forced_lost_lost_lost_lost = 1-forced_lost_lost_lost_won

    not_forced_won_won_won_won = not_forced[4][0][0][0][0]/sum(not_forced[4][0][0][0])
    not_forced_won_won_won_lost = 1-not_forced_won_won_won_won
    not_forced_won_won_lost_won = not_forced[4][0][0][1][0]/sum(not_forced[4][0][0][1])
    not_forced_won_won_lost_lost = 1-not_forced_won_won_lost_won
    not_forced_won_lost_won_won = not_forced[4][0][1][0][0]/sum(not_forced[4][0][1][0])
    not_forced_won_lost_won_lost = 1-not_forced_won_lost_won_won
    not_forced_won_lost_lost_won = not_forced[4][0][1][1][0]/sum(not_forced[4][0][1][1])
    not_forced_won_lost_lost_lost = 1-not_forced_won_lost_lost_won
    not_forced_lost_won_won_won = not_forced[4][1][0][0][0]/sum(not_forced[4][1][0][0])
    not_forced_lost_won_won_lost = 1-not_forced_won_won_won_won
    not_forced_lost_won_lost_won = not_forced[4][1][0][1][0]/sum(not_forced[4][1][0][1])
    not_forced_lost_won_lost_lost = 1-not_forced_lost_won_lost_won
    not_forced_lost_lost_won_won = not_forced[4][1][1][0][0]/sum(not_forced[4][1][1][0])
    not_forced_lost_lost_won_lost = 1-not_forced_lost_lost_won_won
    not_forced_lost_lost_lost_won = not_forced[4][1][1][1][0]/sum(not_forced[4][1][1][1])
    not_forced_lost_lost_lost_lost = 1-not_forced_lost_lost_lost_won

    forced_chance_4_1 = forced_won*forced_won_won*forced_won_won_won*forced_won_won_won_won
    forced_chance_3_2 = forced_won*forced_won_won*forced_won_won_won*forced_won_won_won_lost + forced_won*forced_won_won*forced_won_won_lost*forced_won_won_lost_won + forced_won*forced_won_lost*forced_won_lost_won*forced_won_lost_won_won + forced_lost*forced_lost_won*forced_lost_won_won*forced_lost_won_won_won
    forced_chance_2_3 = forced_won*forced_won_won*forced_won_won_lost*forced_won_won_lost_lost + forced_won*forced_won_lost*forced_won_lost_won*forced_won_lost_won_lost + forced_won*forced_won_lost*forced_won_lost_lost*forced_won_lost_lost_won + forced_lost*forced_lost_won*forced_lost_won_won*forced_lost_won_won_lost + forced_lost*forced_lost_won*forced_lost_won_lost*forced_lost_won_lost_won + forced_lost*forced_lost_lost*forced_lost_lost_won*forced_lost_lost_won_won
    forced_chance_1_4 = forced_won*forced_won_lost*forced_won_lost_lost*forced_won_lost_lost_lost + forced_lost*forced_lost_won*forced_lost_won_lost*forced_lost_won_lost_lost + forced_lost*forced_lost_lost*forced_lost_lost_won*forced_lost_lost_won_lost + forced_lost*forced_lost_lost*forced_lost_lost_lost*forced_lost_lost_lost_won
    forced_chance_0_5 = forced_lost*forced_lost_lost*forced_lost_lost_lost*forced_lost_lost_lost_lost

    not_forced_chance_4_1 = not_forced_won*not_forced_won_won*not_forced_won_won_won*not_forced_won_won_won_won
    not_forced_chance_3_2 = not_forced_won*not_forced_won_won*not_forced_won_won_won*not_forced_won_won_won_lost + not_forced_won*not_forced_won_won*not_forced_won_won_lost*not_forced_won_won_lost_won + not_forced_won*not_forced_won_lost*not_forced_won_lost_won*not_forced_won_lost_won_won + not_forced_lost*not_forced_lost_won*not_forced_lost_won_won*not_forced_lost_won_won_won
    not_forced_chance_2_3 = not_forced_won*not_forced_won_won*not_forced_won_won_lost*not_forced_won_won_lost_lost + not_forced_won*not_forced_won_lost*not_forced_won_lost_won*not_forced_won_lost_won_lost + not_forced_won*not_forced_won_lost*not_forced_won_lost_lost*not_forced_won_lost_lost_won + not_forced_lost*not_forced_lost_won*not_forced_lost_won_won*not_forced_lost_won_won_lost + not_forced_lost*not_forced_lost_won*not_forced_lost_won_lost*not_forced_lost_won_lost_won + not_forced_lost*not_forced_lost_lost*not_forced_lost_lost_won*not_forced_lost_lost_won_won
    not_forced_chance_1_4 = not_forced_won*not_forced_won_lost*not_forced_won_lost_lost*not_forced_won_lost_lost_lost + not_forced_lost*not_forced_lost_won*not_forced_lost_won_lost*not_forced_lost_won_lost_lost + not_forced_lost*not_forced_lost_lost*not_forced_lost_lost_won*not_forced_lost_lost_won_lost + not_forced_lost*not_forced_lost_lost*not_forced_lost_lost_lost*not_forced_lost_lost_lost_won
    not_forced_chance_0_5 = not_forced_lost*not_forced_lost_lost*not_forced_lost_lost_lost*not_forced_lost_lost_lost_lost

    print("--------------------------------")
    print(f"chance of going 4-1 if you force: {forced_chance_4_1*100:.2f}%")
    print(f"chance of going 3-2 if you force: {forced_chance_3_2*100:.2f}%")
    print(f"chance of going 2-3 if you force: {forced_chance_2_3*100:.2f}%")
    print(f"chance of going 1-4 if you force: {forced_chance_1_4*100:.2f}%")
    print(f"chance of going 0-5 if you force: {forced_chance_0_5*100:.2f}%")
    print("--------------------------------")
    print(f"chance of going 4-1 if you don't force: {not_forced_chance_4_1*100:.2f}%")
    print(f"chance of going 3-2 if you don't force: {not_forced_chance_3_2*100:.2f}%")
    print(f"chance of going 2-3 if you don't force: {not_forced_chance_2_3*100:.2f}%")
    print(f"chance of going 1-4 if you don't force: {not_forced_chance_1_4*100:.2f}%")
    print(f"chance of going 0-5 if you don't force: {not_forced_chance_0_5*100:.2f}%")
    print("--------------------------------")
    if "money" in args:
        print(f"average money after going 4-1 if you force: {forced_money[3][0]/forced_scores[3][0]:.1f}k")
        print(f"average money after going 3-2 if you force: {forced_money[3][1]/forced_scores[3][1]:.1f}k")
        print(f"average money after going 2-3 if you force: {forced_money[3][2]/forced_scores[3][2]:.1f}k")
        print(f"average money after going 1-4 if you force: {forced_money[3][3]/forced_scores[3][3]:.1f}k")
        print(f"average money after going 0-5 if you force: {forced_money[3][4]/forced_scores[3][4]:.1f}k")
        print("--------------------------------")
        print(f"average money after going 4-1 if you don't force: {not_forced_money[3][0]/not_forced_scores[3][0]:.1f}k")
        print(f"average money after going 3-2 if you don't force: {not_forced_money[3][1]/not_forced_scores[3][1]:.1f}k")
        print(f"average money after going 2-3 if you don't force: {not_forced_money[3][2]/not_forced_scores[3][2]:.1f}k")
        print(f"average money after going 1-4 if you don't force: {not_forced_money[3][3]/not_forced_scores[3][3]:.1f}k")
        print(f"average money after going 0-5 if you don't force: {not_forced_money[3][4]/not_forced_scores[3][4]:.1f}k")

def printTeamResults(teamForceSuccessRate):
    # team specific data
    teamSuccessRate = []
    for team, rate in teamForceSuccessRate.items():
        if rate[1] > 8:
            teamSuccessRate.append((team, rate, rate[0]/rate[1]))
    
    teamSuccessRate.sort(key=lambda x: x[2], reverse=True)
    print(teamSuccessRate)

if __name__ == "__main__":

    args = {}
    sysargs = [arg.lower() for arg in sys.argv[1:]]
    for argument in sysargs:
        if argument[0] != "-": continue
        if argument[1] == "-": # it's a double -- command
            match argument[2:].lower():
                case "attack":
                    args["attack"] = True
                case "defense":
                    args["defense"] = True
                case "vcl":
                    args["vcl"] = True
                case "teams":
                    args["teams"] = True
                case "round4":
                    args["round4"] = True
                case "round5":
                    args["round5"] = True
                case "maps":
                    args["maps"] = True
                case "first" | "firsthalf":
                    args["first"] = True
                case "second" | "secondhalf":
                    args["second"] = True
                case "money":
                    args["money"] = True
        else: # it's a single - command, so might be multiple commands in one
            i = 1
            while i < len(argument):
                match argument[i].lower():
                    case "a":
                        args["attack"] = True
                    case "d":
                        args["defense"] = True
                    case "t":
                        args["teams"] = True
                    case "r":
                        if i+1 < len(argument) and argument[i+1] in ("4", "5"):
                            args["round" + argument[i+1]] = True
                            i += 1
                    case "f":
                        args["first"] = True
                    case "s":
                        args["second"] = True
                    case "m":
                        args["money"] = True
                i += 1


    if "attack" in args and "defense" in args:
        print("You can't specify only attack and only defense. If you want to show the data for both sides, enter neither argument.")
        exit(1)
    if "first" in args and "second" in args:
        print("You can't specify only frst and second half. If you want to show the data for both halves, enter neither argument.")

    if "vcl" in args:
        with open("VCL_data/data_VCL.json") as file:
            data = orjson.loads(file.read())
    else:
        with open("VCT_data/data_VCT.json") as file:
            data = orjson.loads(file.read())

    if "maps" in args:
        analyzeMapData(data, args=args)
    else:
        analyzeOverallData(data, args=args)

