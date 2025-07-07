from fastapi import APIRouter, Request, Header, HTTPException
from typing import List
import service.acl_service as accessControlService
from domain.entity.entity import IPListModel

router = APIRouter(
    prefix="/gateway"
)


@router.post("/whitelist")
async def set_whitelist(ipList: IPListModel):
    return accessControlService.set_whitelist(ipList)


@router.get("/whitelist")
async def get_whitelist():
    return accessControlService.get_whitelist()


@router.post("/blacklist")
async def set_blacklist(ipList: IPListModel):
    return accessControlService.set_blacklist(ipList)


@router.get("/blacklist")
async def get_blacklist():
    return accessControlService.get_blacklist()
