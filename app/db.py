from sqlalchemy.ext.asyncio import create_async_engine


DATABASE_URL = (
    "postgresql+asyncpg://"
    "ads_user:ads_password@localhost:5433/ads"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)