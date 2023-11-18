import json
import threading
import time
from queue import Queue

import argparse
import requests
from urllib.parse import unquote
from helpers import parse_price
from helpers import Database, Listing

import requests
from urllib import parse
from bs4 import BeautifulSoup

import re


ACTIVITY_URL = "https://steamcommunity.com/market/itemordersactivity"\
               "?item_nameid={item_id}&country=RU&language=english&currency=1&&two_factor=0&norender=1"
db = Database().get_instance()

def get_activities(item_id):
    return requests.get(ACTIVITY_URL.format(item_id=item_id)).json()["activity"]

STEAM_SESSION = "cafea932c9929bccba6f1583"

def getSteamidByAvatarNameAndUsername(user_name, avatar_name):
    timeout=3
    username = user_name
    avatarname = avatar_name.split('/')[3].split(".")[0]

    resp = requests.get("https://steamcommunity.com/search/SearchCommunityAjax?text=" + parse.quote(username) + "&filter=users&sessionid=" + STEAM_SESSION, headers={"Cookie": "sessionid=" + STEAM_SESSION}, timeout=timeout)
    data = resp.json()
    soup = BeautifulSoup(data["html"], "html.parser")
    for div in soup.find_all('div', class_='avatarMedium'):
        img = div.find('img')

        imgFileName = img['src'].rsplit('/', 1)
        imgName = imgFileName[1].split('_', 1)[0]

        if imgName == avatarname:
            return div.find('a')['href'].rsplit("/", 1)[1]
    
    return ""

def get_profile_link(steamIdOrUsername):
    if re.match(r'^\d+$', steamIdOrUsername):
        url = "https://steamcommunity.com/profiles/" + steamIdOrUsername
    else:
        url = "https://steamcommunity.com/id/" + steamIdOrUsername
    return url

def worker(queue):
    while True:
        listing_id, listing_link = queue.get()
        for activity in get_activities(listing_id):
            if activity["type"] == "BuyOrderCancel" or activity["type"] == "BuyOrderMulti":
                continue
            
            item_name=unquote(listing_link.split('/')[6])
            price=parse_price(activity["price"])
            owner_name=activity["persona_seller"] or activity["persona_buyer"]
            owner_avatar=activity["avatar_seller"] or activity["avatar_buyer"]
            
            steamIdOrUsername=getSteamidByAvatarNameAndUsername(owner_name, owner_avatar)
            
            url=get_profile_link(steamIdOrUsername)
            if url is None:
                continue
            else:
                rrr = requests.get(url)
                soup1 = BeautifulSoup(rrr.content, 'html.parser')
                situation = soup1.find('div', class_ = 'profile_in_game_header')
                if situation is None:
                    continue
                else:
                    online = situation.text.split(' ')[1]
                    if online == 'Offline':
                        continue
                    else:
                        listing = Listing(
                            item_name=item_name,
                            price=price,
                            owner_name=owner_name,
                            owner_avatar=owner_avatar,
                            profile_link=url
                        )
                        db.insert_listing(listing)
                time.sleep(10)
        queue.put((listing_id, listing_link))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--threadCount", type=int, default=10
    )
    args = parser.parse_args()

    print("Total Threads: ", args.threadCount)
    with open('listings.json', 'r', encoding='utf-8') as f:
        listings = json.load(f)

    queue = Queue()

    for listing_link, listing_id in listings.items():
        queue.put((listing_link, listing_id))

    for _ in range(args.threadCount):
        threading.Thread(target=worker, args=(queue,)).start()
    # worker(queue)