#!/usr/bin/env python3
"""Seed the database with initial data for development."""

import asyncio
import os

from app.common.database import get_session_factory
from app.common.security import generate_salt, hash_password
from app.domains.identity.model import User


async def seed() -> None:
    factory = get_session_factory()
    async with factory() as session:
        salt = generate_salt()
        admin = User(
            email="admin@example.com",
            hashed_password=hash_password("Admin123", salt),
            password_salt=salt,
            is_superuser=True,
        )
        session.add(admin)

        salt2 = generate_salt()
        user = User(
            email="user@example.com",
            hashed_password=hash_password("User1234", salt2),
            password_salt=salt2,
        )
        session.add(user)

        await session.commit()
        print(f"Created admin: admin@example.com / Admin123")
        print(f"Created user:  user@example.com / User1234")


if __name__ == "__main__":
    os.environ.setdefault("DB_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/app")
    asyncio.run(seed())
