from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import AdminCreateModel, UserCreateModel, UserModel, UserLoginModel, UserBooksModel, EmailModel, PasswordResetRequestModel, PasswordResetConfirmModel, UserRoleUpdateModel, UserPublicModel
from .service import UserService
from src.db.main import get_session
from fastapi.exceptions import HTTPException
from .utils import create_access_token, decode_token, verify_password,create_url_safe_token, decode_url_safe_token, generate_password_hash
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from src.db.redis import add_jti_to_blocklist
from src.errors import UserAlreadyExists, UserNotFound, InvalidCredentials, InvalidToken
from src.mail import mail, create_message
from src.config import Config
from src.celery_tasks import send_email
from src.constants import ACCESS_TOKEN_EXPIRY_MINUTES, REFRESH_TOKEN_EXPIRY_DAYS


auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin","user"])
admin_role_checker = RoleChecker(["admin"])

def _auth_link(path: str, token: str) -> str:
    scheme = Config.APP_SCHEME
    return f"{scheme}://{Config.DOMAIN}{path.format(token=token)}"

@auth_router.post('/send_mail')
async def send_mail(
    emails: EmailModel,
    _: bool = Depends(admin_role_checker),
):
    emails_list = [str(e).strip() for e in emails.addresses]
    html = "<h1>Welcome to the app</h1>"
    subject = "Welcome to the app"
    send_email.delay(emails_list, subject, html)
    return {"message":"Email sent successfully"}
    

@auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def create_user_Account(user_data: UserCreateModel, bg_tasks: BackgroundTasks, session:AsyncSession = Depends(get_session)) :
    email = str(user_data.email).strip()
    user_exists = await user_service.user_exists(email, session)
    if user_exists : 
        raise UserAlreadyExists()

    # Determine role based on admin_key
    admin_key = user_data.admin_key
    if admin_key:
        if not Config.ADMIN_SECRET_KEY or admin_key != Config.ADMIN_SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid admin secret key"
            )
        role = "admin"
        is_verified = True  # Admins are auto-verified
    else:
        role = "user"
        is_verified = False

    new_user = await user_service.create_user(user_data, session, role=role, is_verified=is_verified)

    if role == "user":
        token = create_url_safe_token({"email":email})
        link = _auth_link("/api/v1/auth/verify/{token}", token)
        html_message = f"""
        <h1>Verify your Email</h1>
        <p>Please click this <a href="{link}">link</a> to verify your email</p>
        """
        emails = [email]
        subject = "Verify Your email"
        send_email.delay(emails, subject, html_message)

    return {
        "message": "Admin account created successfully" if role == "admin" else "Account Created! Check email to verify your account",
        "user": new_user
    }


@auth_router.post('/admin/signup', status_code=status.HTTP_201_CREATED)
async def create_admin_account(
    user_data: AdminCreateModel,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    email = str(user_data.email).strip()
    user_exists = await user_service.user_exists(email, session)
    if user_exists:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session, role="admin", is_verified=True)
    return JSONResponse(
        content={
            "message": "Admin account created successfully",
            "user": {
                "username": new_user.username,
                "email": new_user.email,
                "role": new_user.role,
            },
        },
        status_code=status.HTTP_201_CREATED,
    )

@auth_router.get('/verify/{token}')
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    if not token_data:
        raise InvalidToken()

    user_email = token_data.get("email")
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()
        await user_service.update_user(user, {"is_verified": True}, session)
        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )

    raise InvalidToken()

@auth_router.post('/login')
async def login_users(
                    login_data: UserLoginModel,
                    session: AsyncSession = Depends(get_session)
                    ):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)
        
        if password_valid:
            access_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid),
                    'role': user.role
                },
                refresh=False,
                expiry=timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)
            )
            refresh_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid)
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS)
            )
            
            return JSONResponse(
                content={
                    "message": "Login successfully",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": user.email,
                        "uid": str(user.uid),
                        "role": user.role
                    }
                }
            )
    
    raise InvalidCredentials()

@auth_router.get('/refresh_token')
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer()), session: AsyncSession = Depends(get_session)):
    user_email = token_details["user"]["email"]
    user = await user_service.get_user_by_email(user_email, session)
    if not user:
        raise UserNotFound()

    new_access_token = create_access_token(
        user_data={
            "email": user.email,
            "user_uid": str(user.uid),
            "role": user.role
        },
        expiry=timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES),
    )
    return JSONResponse(content={
            "access_token": new_access_token
        }
    )

@auth_router.get('/me',response_model=UserBooksModel)
async def get_currentUser(user = Depends(get_current_user), role_checker: bool = Depends(role_checker)):
    return user 




@auth_router.get('/logout')
async def revoke_token(token_details:dict = Depends(AccessTokenBearer())):
    jti = token_details['jti']
    await add_jti_to_blocklist(jti)
    return JSONResponse(
        content={
            "message":"logged Out Successfully"
        },
        status_code=status.HTTP_200_OK
    )

"""
1. PROVIDE THE EMAIL -> password reset request
2. SEND PASSWORD RESET LINK
3. RESET PASSWORD -> password reset confirm
"""

@auth_router.post('/password-reset-request')
async def password_reset_request(
    email_data: PasswordResetRequestModel,
    session: AsyncSession = Depends(get_session),
):
    email = email_data.email.strip()
    user = await user_service.get_user_by_email(email, session)
    if user:
        token = create_url_safe_token({"email": email})
        link = _auth_link("/api/v1/auth/password-reset-confirm/{token}", token)
        html_message = f"""
        <h1>Reset Your Password</h1>
        <p>Please click this <a href="{link}">link</a> to reset your password</p>
        """
        send_email.delay([email], "Reset Your Password", html_message)
    return JSONResponse(
        content={
            "message": "If an account exists for that email, reset instructions have been sent."
        },
        status_code=status.HTTP_200_OK
    )

@auth_router.post('/password-reset-confirm/{token}')
async def reset_account_password(token: str, passwords: PasswordResetConfirmModel, session: AsyncSession = Depends(get_session)):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_new_password
    if new_password != confirm_password :
        raise HTTPException(
            detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST
        )
    token_data = decode_url_safe_token(token)
    if not token_data:
        raise InvalidToken()

    user_email = token_data.get("email")
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()
        passwd_hash = generate_password_hash(new_password)
        await user_service.update_user(user, {"password_hash": passwd_hash}, session)
        return JSONResponse(
            content={"message": "Password Reset successfully"},
            status_code=status.HTTP_200_OK,
        )

    raise InvalidToken()

@auth_router.get('/users', response_model=list[UserPublicModel])
async def get_all_users(
    session: AsyncSession = Depends(get_session),
    admin_access: bool = Depends(admin_role_checker)
):
    users = await user_service.get_all_users(session)
    return users

@auth_router.patch('/users/{uid}/role', response_model=UserPublicModel)
async def update_user_role(
    uid: str,
    role_data: UserRoleUpdateModel,
    session: AsyncSession = Depends(get_session),
    admin_access: bool = Depends(admin_role_checker)
):
    user = await user_service.get_user_by_uid(uid, session)
    if not user:
        raise UserNotFound()
    
    updated_user = await user_service.update_user(user, {"role": role_data.role}, session)
    return updated_user

@auth_router.delete('/users/{uid}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    uid: str,
    session: AsyncSession = Depends(get_session),
    admin_access: bool = Depends(admin_role_checker)
):
    user = await user_service.get_user_by_uid(uid, session)
    if not user:
        raise UserNotFound()
    
    await user_service.delete_user(user, session)
    return None