import requests
import time
from bs4 import BeautifulSoup
import random

matchIDs = []
with open(f"VCL_data/VCL_matchIDs.txt", "r") as file:
    matchIDs += file.read().splitlines()

with open(f"VCL_data/data_VCL.py", "w") as file:
    wait = 0
    file.write("data = [\n")
    for i in range(len(matchIDs)):
        matchID = matchIDs[i]
        print("parsing match " + matchID + "...")
        foundMatch = False
        attempts = 0
        while not foundMatch:
            try:
                response = requests.get(f"https://www.vlr.gg/" + matchID)
                foundMatch = True
            except:
                attempts += 1
                if attempts >= 5:
                    print("giving up")
                    exit(1)
                print("response error occured, waiting 5 seconds before trying again.")
                time.sleep(5)


        if response.status_code == 429:
            print("TOO FAST")
            exit(1)
        elif response.status_code != 200:
            print("ERROR")
            print(response.text)
            exit(1)
        soup = BeautifulSoup(response.text, 'html.parser')

        foundMatch = False
        attempts = 0
        while not foundMatch:
            try:
                response = requests.get(f"https://www.vlr.gg/" + matchID + "?tab=economy")
                foundMatch = True
            except:
                attempts += 1
                if attempts >= 5:
                    print("giving up")
                    exit(1)
                print("response error occured, waiting 5 seconds before trying again.")
                time.sleep(5)


        if response.status_code == 429:
            print("TOO FAST")
            exit(1)
        elif response.status_code != 200:
            print("ERROR")
            print(response.text)
            exit(1)
        soupEconomy = BeautifulSoup(response.text, 'html.parser')

        matchData = {}

        for gameCover in soupEconomy.find('div', class_='vm-stats-container').find_all('div', class_='vm-stats-game'):
            gameID = gameCover["data-game-id"]
            if gameID == 'all':
                continue

            table = gameCover.find_all('table', class_='wf-table-inset')
            if len(table) == 0:
                # this map is not available (always means it wasn't played afaik)
                continue

            table = table[1].find_all('td')
            teamNames = [name.text.strip() for name in table[0].find_all('div', class_='team')]

            roundEcos = []
            roundSpent = []
            for td in table[1:]:
                Round = td.find_all('div', class_='rnd-sq')
                if len(Round) == 0:
                    # not a real round
                    continue

                roundEcos.append([float(bank.text.strip()[:-1]) for bank in td.find_all('div', class_='bank')])
                roundSpent.append([r.text.count("$") for r in Round])

            matchData[gameID] = {"roundEcos": roundEcos, "roundSpent": roundSpent}


        for gameCover in soup.find('div', class_='vm-stats-container').find_all('div', class_='vm-stats-game'):
            gameID = gameCover["data-game-id"]
            if gameID == 'all' or gameID not in matchData: # if it's the overall data or there was no economy data saved
                continue
            gameHeader = gameCover.find('div', class_='vm-stats-game-header')
            mapName = gameHeader.find('div', class_='map').div.span.text.strip().split("\t")[0] # :)

            vlrRounds = gameCover.find('div', class_='vlr-rounds').find_all('div', class_='vlr-rounds-row-col')

            roundWins = []
            roundWinMethods = []
            teams = [name.text.strip() for name in vlrRounds[0].find_all('div', class_='team')]

            for td in vlrRounds[1:]:
                if (not td.has_attr('title')) or td['title'] == "":
                    # it's not a real round
                    continue
                Round = td.find_all('div', class_='rnd-sq')
                if len(Round) == 0: continue
                if "mod-win" in Round[0]["class"]:
                    roundWins.append([teamNames[0],])
                    winnerDiv = Round[0]
                else:
                    roundWins.append([teamNames[1],])
                    winnerDiv = Round[1]

                if "mod-ct" in winnerDiv["class"]:
                    roundWins[-1].append("ct")
                else:
                    roundWins[-1].append("t")
                roundWinMethods.append(winnerDiv.find("img")["src"][20:-5])

                    
            file.write(str({"matchID": matchID,
                            "gameID": gameID,
                            "teams": teamNames,
                            "map": mapName,
                            "roundWins": roundWins,
                            "roundWinMethods": roundWinMethods,
                            "roundEcos": matchData[gameID]["roundEcos"],
                            "roundSpent": matchData[gameID]["roundSpent"]
                           }))
            file.write(",\n")

        wait += 1
        if wait > 6:
            time.sleep(0.5 + 1.25*random.random())
            wait = 0
        print(f"{len(matchIDs)-i-1} matches left")

    file.write("]\n")

