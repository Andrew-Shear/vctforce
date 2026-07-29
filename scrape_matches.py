import requests
import re
import time
import json
from bs4 import BeautifulSoup
import random
from VCL_data import VCL_events

#events = ["1924", "2097", "2095", "2096", "2005", "2094", "1999", "2006", "2004", "1998", "2002", "1921", "1923", "1926", "1925"] # 2024
#events = ["1657", "1658", "1659", "1660", "1664", "1494", "1189", "1190", "1191", "1188"] # 2023
#events = ["2283", "2501", "2498", "2500", "2499", "2282", "2380", "2379", "2359", "2347", "2281", "2276", "2277", "2274", "2275"] # 2025
#events = ["2765", "2860", "2863", "2775", "2864", "2760", "2682", "2684", "2683", "2685"] # 2026 up to london

#events = []
#for i in range(1, 6):
#    response = requests.get(f"https://vlr.gg/events/?tier=61&page={i}")
#    if response.status_code == 429:
#        print("TOO FAST")
#        exit(1)
#    elif response.status_code != 200:
#        print("ERROR")
#        print(response.text)
#        exit(1)
#    soup = BeautifulSoup(response.text, 'html.parser')
#    events += [event["href"].split("/")[2] for event in soup.find_all('a', class_='mod-flex')]
#
#with open("VCL_events.py", "w") as file:
#    file.write("events = ")
#    file.write(str(events))
#exit(0)

wait = 0
with open("VCL_data/VCL_matchIDs.py", "w") as file:
    for i in range(len(VCL_events.events)):
        event = VCL_events.events[i]
        response = requests.get(f"https://vlr.gg/event/matches/" + event)
        if response.status_code == 429:
            print("TOO FAST")
            exit(1)
        elif response.status_code != 200:
            print("ERROR")
            print(response.text)
            exit(1)
        soup = BeautifulSoup(response.text, 'html.parser')
        for match in soup.find_all('a', class_='wf-module-item'):
            file.write(re.match(r"/(\d+)/.*", match["href"]).group(1))
            file.write("\n")
        wait += 1
        if wait > 5:
            time.sleep(1 + 1.5*random.random())
            wait = 0

        print(f"{len(VCL_events.events)-i-1} events left")

