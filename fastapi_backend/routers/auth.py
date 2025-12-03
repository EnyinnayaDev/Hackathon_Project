from fastapi import APIRouter
from services.origin_service import origin_service

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/socials")
async def get_linked_socials():
    """Get user's linked social accounts from Origin"""
    result = await origin_service.get_linked_socials()
    return result

@router.get("/twitter/{username}")
async def get_twitter_user(username: str):
    """Get Twitter user data from Origin"""
    result = await origin_service.get_twitter_user(username)
    return result