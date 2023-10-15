#!/usr/bin/env python3
import threading
import time
from queue import Queue
import argparse
import traceback
from helpers import Database, Listing, get_player_summaries


# set range for steamids to fetch (you can create new account to find last id)
try:
    with open('.steamidcount', 'r') as f:
        STEAMIDS_START = int(f.read())
except:
    STEAMIDS_START = 76561197960265729
STEAMIDS_END = 76561199080098567

db = Database().get_instance()

def worker(queue):
    global request_count

    while True:
        steamids = queue.get()
        while True:
            try:
                summaries = get_player_summaries(steamids, timeout=30)
                db.insert_profiles(summaries)
                request_count += 1
            except:
                traceback.print_exc()


def feed(queue):
    for i in range(STEAMIDS_START, STEAMIDS_END, 100):
        queue.put([k for k in range(i, i+100)])
        with open('.steamidcount', 'w+') as f:
            f.write(str(i))
        while queue.qsize() > 10000:
            time.sleep(0.001)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--threadCount", type=int, default=50)

    args = parser.parse_args()

    queue = Queue()
    request_count = 0

    threading.Thread(target=feed, args=(queue,)).start()

    for _ in range(args.threadCount):
        threading.Thread(target=worker, args=(queue,)).start()

    while True:
        #print(f"{request_count} request")
        request_count = 0
        time.sleep(60)
