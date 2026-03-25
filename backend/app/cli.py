import argparse
import asyncio

from app.db.bootstrap import bootstrap_system_admin
from app.db.session import async_session_factory, engine
from app.models.base import Base


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_factory() as session:
        await bootstrap_system_admin(session)


def main() -> None:
    parser = argparse.ArgumentParser(description="尚图工坊数据库与管理员初始化命令")
    parser.add_argument("command", choices=["init-db"])
    args = parser.parse_args()
    if args.command == "init-db":
        asyncio.run(init_db())


if __name__ == "__main__":
    main()
