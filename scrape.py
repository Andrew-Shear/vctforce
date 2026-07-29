import requests
import re
import time
import json
from bs4 import BeautifulSoup
import random

matchIDs = []
with open(f"VCL_data/VCL_matchIDs.txt", "r") as file:
    matchIDs = file.read().splitlines()

with open(f"VCL_data/data_VCL.py", "w") as file:
    wait = 0
    file.write("data = [\n")
    for i in range(len(matchIDs)):
        match_id = matchIDs[i]
        response = requests.get(f"https://www.vlr.gg/" + match_id + "?tab=economy")
        if response.status_code == 429:
            print("TOO FAST")
            exit(1)
        elif response.status_code != 200:
            print("ERROR")
            print(response.text)
            exit(1)
        soup = BeautifulSoup(response.text, 'html.parser')
        mapNames = []
        for mapBox in soup.find_all('div', class_='vm-stats-gamesnav-item')[1:]:
            mapNames.append(mapBox.div.text.strip()[1:].strip()) # lol

        mapNameIndex = 0
        for tableCover in soup.find_all('table', class_='wf-table-inset mod-econ')[1::2]:
            table = tableCover.find_all('td')
            teamNames = [name.text.strip() for name in table[0].find_all('div', class_='team')]
            roundEcos = []
            roundWins = []
            roundSpent = []
            for td in table[1:]:
                Round = td.find_all('div', class_='rnd-sq')
                if len(Round) == 0: continue
                if "mod-win" in Round[0]["class"]:
                    roundWins.append([teamNames[0],])
                else:
                    roundWins.append([teamNames[1],])
                if "mod-ct" in Round[0]["class"] or "mod-ct" in Round[1]["class"]: # the defense won this round
                    roundWins[-1].append("ct")
                else:
                    roundWins[-1].append("t")

                roundEcos.append([float(bank.text.strip()[:-1]) for bank in td.find_all('div', class_='bank')])
                roundSpent.append([r.text.count("$") for r in Round])
                    
            file.write(str({"link": response.url, "teams": teamNames, "map": mapNames[mapNameIndex], "roundWins": roundWins, "roundEcos": roundEcos, "roundSpent": roundSpent}))
            file.write(",\n")
            mapNameIndex += 1

        wait += 1
        if wait > 8:
            time.sleep(1 + 1.5*random.random())
            wait = 0
        print(f"{len(matchIDs)-i-1} matches left")

    file.write("]\n")

