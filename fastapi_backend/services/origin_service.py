import httpx
from config import settings

class OriginService:
    def __init__(self):
        self.base_url = settings.node_service_url
    
    async def check_health(self):
        """Check if Node microservice is healthy"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health", timeout=5.0)
                return response.json()
        except Exception as e:
            return {"error": str(e), "connected": False}
    
    async def get_linked_socials(self):
        """Get user's linked social accounts"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/auth/socials")
                return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def get_twitter_user(self, username: str):
        """Get Twitter user data"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/twitter/user/{username}")
                return response.json()
        except Exception as e:
            return {"error": str(e)}

origin_service = OriginService()