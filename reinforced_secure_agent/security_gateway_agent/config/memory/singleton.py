from typing import List
from domain.entity.entity import IPListModel


# 나중에 이중화 또는 3중화할때는 Redis로 연동하는 계획으로 가자
class WhiteList:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print("\nWhiteList Memory is generated")
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, "_init"):
            print("WhiteList Memory is initialized\n")
            self._whitelist = []
            cls._init = True

    def reset_whitelist(self) -> None:
        self._whitelist = []

    def get_whitelist(self) -> List[str]:
        return self._whitelist

    def add_whitelist(self, ip_list_model: IPListModel) -> None:
        ip_address_list = ip_list_model.ipList
        ip_address_list.extend(self._whitelist)
        ip_address_list = list(set(ip_address_list))
        self._whitelist = ip_address_list


class Blacklist:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print("\nBlacklist Memory is generated")
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, "_init"):
            print("Blacklist Memory is initialized\n")
            self._blacklist = []
            cls._init = True

    def reset_blacklist(self) -> None:
        self._blacklist = []

    def get_blacklist(self) -> List[str]:
        return self._blacklist

    def add_blacklist(self, ip_list_model: IPListModel) -> None:
        ip_address_list = ip_list_model.ipList
        ip_address_list.extend(self._blacklist)
        ip_address_list = list(set(ip_address_list))
        self._blacklist = ip_address_list
