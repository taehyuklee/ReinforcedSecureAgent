from pydantic import BaseModel
from typing import List


class IPListModel(BaseModel):
    ipList: List[str]
