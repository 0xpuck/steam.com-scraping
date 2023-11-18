import datetime
import os
import time
from typing import List

import psycopg2

api_key = os.getenv("API_KEY")
api_key = "3A21E339E784994D3772723F327FC337"


class Database:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = Database()
        return cls._instance

    def __init__(self):
        self.connection = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="12345678",
            port="5432",
        )
        self.cursor = self.connection.cursor()

    def insert_listing(self, lst):
        avatar = parse_hash_from_link(lst.owner_avatar)
        self.cursor.execute(
            "INSERT INTO listings(item_name, time, price, owner_name, owner_avatar, profile_link) "
            f"VALUES ( %s, now(), {lst.price}, %s, '{avatar}', %s)"
            " ON CONFLICT DO NOTHING", (lst.item_name, lst.owner_name, lst.profile_link)
        )
        self.connection.commit()
        if self.cursor.rowcount:
            print(
                f"{datetime.datetime.now()} {lst.item_name: <60} ${lst.price: <4} {lst.owner_name} {lst.profile_link}")

    def get_listings(self, minprice=0, maxprice=-1, limit=50):
        conditions = [
            f" price > {minprice} ",
            f" price < {maxprice} " if maxprice != -1 else "true",
        ]
        self.cursor.execute(
            f"SELECT * FROM listings WHERE {' AND '.join(conditions)} ORDER BY id DESC LIMIT {limit}")
        # print(f"SELECT * FROM listings WHERE {' AND '.join(conditions)} ORDER BY id DESC LIMIT {limit}")

        out = []
        for row in self.cursor.fetchall():
            listing = Listing(
                id=row[0],
                item_name=row[1],
                time=row[2],
                price=row[3],
                owner_name=row[4],
                owner_avatar=row[5],
                profile_link=row[6]
            )
            out.append(listing)
        # print("\n\nimg data out >>>> ", out)
        return out

class Listing:
    item_name: str
    time: str
    price: int
    owner_name: str
    owner_avatar: str
    profile_link: str

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return f"{self.item_name} {self.price} {self.owner_name}"

def parse_hash_from_link(link):
    return link.split('/')[3]

def parse_price(string):
    return int(string[1:].replace(",", "").split('.')[0])