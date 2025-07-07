from typing import List
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from config.memory.singleton import WhiteList, Blacklist
from domain.entity.entity import IPListModel

# 나중에 Redis로 변경될 부분
whitelist = WhiteList()
blacklist = Blacklist()


def set_whitelist(ip_address_list: IPListModel) -> List[str]:
    global whitelist

    whitelist.add_whitelist(ip_address_list)
    return whitelist.get_whitelist()


def get_whitelist() -> List[str]:
    global whitelist

    return whitelist.get_whitelist()


def set_blacklist(ip_address_list: IPListModel) -> List[str]:
    global blacklist
    import ast
    print(str(ip_address_list) + " 해당 주소는 BlackList에 추가됩니다")
    blacklist.add_blacklist(ip_address_list)
    return blacklist.get_blacklist()


def get_blacklist() -> List[str]:
    global blacklist
    return blacklist.get_blacklist()
