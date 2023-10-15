#!/usr/bin/env python3
import json
import os
import threading
import time
from queue import Queue

import argparse
import requests
from urllib.parse import unquote
from helpers import parse_price
import traceback
from helpers import Database, Listing


ACTIVITY_URL = "https://steamcommunity.com/market/itemordersactivity"\
               "?item_nameid={item_id}&country=RU&language=english&currency=1&&two_factor=0&norender=1"
db = Database().get_instance()

def get_activities(item_id):
    response = requests.get(ACTIVITY_URL.format(item_id=item_id))
    if response.status_code == 200:
        return response.json()["activity"]
    else:
        print("api steam error")
    return []


def worker(queue):
    while True:
        listing_id, listing_link = queue.get()

        for activity in get_activities(listing_id):
            if activity["type"] == "BuyOrderCancel" or activity["type"] == "BuyOrderMulti":
                continue
            listing = Listing(
                game=int(listing_link.split('/')[5]),
                item_name=unquote(listing_link.split('/')[6]),
                price=parse_price(activity["price"]),
                owner_name=activity["persona_seller"] or activity["persona_buyer"],
                owner_avatar=activity["avatar_seller"] or activity["avatar_buyer"]
            )
            db.insert_listing(listing)

        queue.put((listing_id, listing_link))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--threadCount", type=int, default=60
    )
    args = parser.parse_args()

    print("Total Threads: ", args.threadCount)
    with open('listings.json', 'r') as f:
        listings = json.load(f)

    queue = Queue()

    for listing_id, listing_link in listings.items():
        queue.put((listing_link, listing_id))

    for _ in range(args.threadCount):
        threading.Thread(target=worker, args=(queue,)).start()

