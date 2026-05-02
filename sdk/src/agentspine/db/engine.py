"""Async database and redis connection pools."""

import structlog
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

logger = structlog.get_logger()


class DatabasePool:
    """Async connection pool for PostgreSQL."""

    def __init__(self, url: str, pool_size: int = 10, max_overflow: int = 20):
        self._url = url
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None

    async def connect(self) -> None:
        if self.engine:
            return

        self.engine = create_async_engine(
            self._url,
            pool_size=self._pool_size,
            max_overflow=self._max_overflow,
            echo=False,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("db.connected", pool_size=self._pool_size)

    async def disconnect(self) -> None:
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.session_factory = None
            logger.info("db.disconnected")

    def session(self) -> AsyncSession:
        if not self.session_factory:
            raise RuntimeError("DatabasePool not connected")
        return self.session_factory()


class RedisPool:
    """Async connection pool for Redis."""

    def __init__(self, url: str):
        self._url = url
        self._redis = None

    async def connect(self) -> None:
        if self._redis:
            return

        from redis.asyncio import Redis
        self._redis = Redis.from_url(self._url, decode_responses=True)
        # Verify connection
        await self._redis.ping()
        logger.info("redis.connected")

    async def disconnect(self) -> None:
        if self._redis:
            await self._redis.aclose()
            self._redis = None
            logger.info("redis.disconnected")

    def get_client(self):
        if not self._redis:
            raise RuntimeError("RedisPool not connected")
        return self._redis
