from src.db.models import User
from .schemas import UserCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from .utils import generate_password_hash


class UserService :
    async def get_user_by_email(self,email: str, session: AsyncSession) :
        statement = select(User).where(User.email == email)

        result = await session.exec(statement)

        user = result.first()

        return user
    async def user_exists(self,email, session:AsyncSession) :
        user = await self.get_user_by_email(email,session)
        return True if user is not None else False
    async def create_user(self, user_data: UserCreateModel, session: AsyncSession, role: str = "user", is_verified: bool = False):
        user_data_dict = user_data.model_dump()
        password = user_data_dict.pop('password')
        user_data_dict.pop('admin_key', None)  # Remove admin_key — not a DB column
        new_user = User(
            **user_data_dict
        )
        new_user.password_hash = generate_password_hash(password)
        new_user.role = role
        new_user.is_verified = is_verified
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    
    async def update_user(self, user: User, user_data: dict, session: AsyncSession):
        for k, v in user_data.items():
            setattr(user, k, v)
        await session.commit()
        await session.refresh(user)
        return user

    async def get_all_users(self, session: AsyncSession):
        statement = select(User).order_by(User.created_at.desc())
        result = await session.exec(statement)
        return result.all()

    async def get_user_by_uid(self, uid: str, session: AsyncSession):
        statement = select(User).where(User.uid == uid)
        result = await session.exec(statement)
        return result.first()

    async def delete_user(self, user: User, session: AsyncSession):
        await session.delete(user)
        await session.commit()
        return True