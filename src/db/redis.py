import redis.asyncio as aioredis
from src.config import Config
from src.constants import JTI_BLOCKLIST_EXPIRY_SECONDS

token_blocklist = aioredis.from_url(Config.REDIS_URL)

async def add_jti_to_blocklist(jti: str) -> None :
    await token_blocklist.set(
        name=jti,
        value="",
        ex=JTI_BLOCKLIST_EXPIRY_SECONDS
    )

async def token_in_blocklist(jti: str) -> bool :
    jti = await token_blocklist.get(jti)
    return jti is not None


