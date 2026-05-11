from sqlalchemy import select

from app.common.base.repository import BaseRepository
from app.domains.identity.model import User


class UserRepository(BaseRepository[User]):
    model_class = User

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_oidc(self, provider: str, sub: str) -> User | None:
        stmt = select(User).where(
            User.oidc_provider == provider,
            User.oidc_sub == sub,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
