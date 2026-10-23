from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from src.config import Config
from src.constants import ACCESS_TOKEN_EXPIRY_SECONDS, EMAIL_TOKEN_MAX_AGE_SECONDS
import uuid
import logging
from itsdangerous import URLSafeTimedSerializer

passwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def generate_password_hash(passwd: str) -> str:
    return passwd_context.hash(passwd)

def verify_password(password: str, hashed_password: str) -> bool:
    return passwd_context.verify(password, hashed_password)

def create_access_token(user_data: dict,expiry: timedelta | None = None, refresh: bool = False) :
    if expiry is None:
        expiry = timedelta(seconds=ACCESS_TOKEN_EXPIRY_SECONDS)
    payload = {}

    payload['user'] = user_data
    payload['exp'] = datetime.now(timezone.utc)+expiry 
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh

    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM)
    return token
def decode_token(token: str) -> dict :
    try :
        token_data = jwt.decode(
            jwt= token,
            key= Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWTError as e :
        logging.exception(e)
        return None

serializer = URLSafeTimedSerializer(
        secret_key=Config.JWT_SECRET,
        salt="email-configuration"
    )
def create_url_safe_token(data: dict) :
    token = serializer.dumps(data, salt="email-configuration")
    return token
def decode_url_safe_token(token: str) :
    try:
        return serializer.loads(token, max_age=EMAIL_TOKEN_MAX_AGE_SECONDS)
    except Exception as e:
        logging.error(str(e))
        return None