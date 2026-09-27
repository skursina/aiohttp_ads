from aiohttp import web
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select

from app.db import engine
from app.models import Advertisement, User

from app.auth import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


Session = async_sessionmaker(engine, expire_on_commit=False)


async def create_ad(request):
    user_id = get_current_user_id(request)

    if user_id is None:
        return web.json_response(
            {"error": "Authentication required"},
            status=401,
        )

    data = await request.json()

    title = data.get("title")
    description = data.get("description")

    if not title or not description:
        return web.json_response(
            {"error": "title and description are required"},
            status=400,
        )

    async with Session() as session:
        ad = Advertisement(
            title=title,
            description=description,
            owner_id=user_id,
        )

        session.add(ad)
        await session.commit()
        await session.refresh(ad)

    return web.json_response(
        {
            "id": ad.id,
            "title": ad.title,
            "description": ad.description,
            "created_at": ad.created_at.isoformat(),
            "owner_id": ad.owner_id,
        },
        status=201,
    )


async def get_ad(request):
    ad_id = int(request.match_info["ad_id"])

    async with Session() as session:
        result = await session.execute(
            select(Advertisement).where(Advertisement.id == ad_id)
        )

        advertisement = result.scalar_one_or_none()

        if advertisement is not None:
            await session.refresh(advertisement, ["user"])

    if advertisement is None:
        return web.json_response(
            {"error": "Advertisement not found"},
            status=404,
        )

    return web.json_response(
        {
            "id": advertisement.id,
            "title": advertisement.title,
            "description": advertisement.description,
            "created_at": advertisement.created_at.isoformat(),
            "owner_id": advertisement.owner_id,
            "owner_email": advertisement.user.email,
        }
    )


async def get_ads(request):
    async with Session() as session:
        result = await session.execute(
            select(Advertisement).order_by(Advertisement.id)
        )

        advertisements = result.scalars().all()

        for advertisement in advertisements:
            await session.refresh(advertisement, ["user"])

    return web.json_response(
        [
            {
                "id": advertisement.id,
                "title": advertisement.title,
                "description": advertisement.description,
                "created_at": advertisement.created_at.isoformat(),
                "owner_id": advertisement.owner_id,
                "owner_email": advertisement.user.email,
            }
            for advertisement in advertisements
        ]
    )


async def update_ad(request):
    user_id = get_current_user_id(request)

    if user_id is None:
        return web.json_response(
            {"error": "Authentication required"},
            status=401,
        )

    ad_id = int(request.match_info["ad_id"])

    data = await request.json()

    async with Session() as session:
        result = await session.execute(
            select(Advertisement).where(Advertisement.id == ad_id)
        )

        advertisement = result.scalar_one_or_none()

        if advertisement is None:
            return web.json_response(
                {"error": "Advertisement not found"},
                status=404,
            )

        if advertisement.owner_id != user_id:
            return web.json_response(
                {"error": "You are not the owner of this advertisement"},
                status=403,
            )

        if "title" in data:
            advertisement.title = data["title"]

        if "description" in data:
            advertisement.description = data["description"]

        await session.commit()
        await session.refresh(advertisement)

    return web.json_response({
        "id": advertisement.id,
        "title": advertisement.title,
        "description": advertisement.description,
        "created_at": advertisement.created_at.isoformat(),
        "owner_id": advertisement.owner_id,
    })


async def delete_ad(request):
    user_id = get_current_user_id(request)

    if user_id is None:
        return web.json_response(
            {"error": "Authentication required"},
            status=401,
        )

    ad_id = int(request.match_info["ad_id"])

    async with Session() as session:
        result = await session.execute(
            select(Advertisement).where(Advertisement.id == ad_id)
        )

        advertisement = result.scalar_one_or_none()

        if advertisement is None:
            return web.json_response(
                {"error": "Advertisement not found"},
                status=404,
            )

        if advertisement.owner_id != user_id:
            return web.json_response(
                {"error": "You are not the owner of this advertisement"},
                status=403,
            )

        await session.delete(advertisement)
        await session.commit()

    return web.Response(status=204)


def get_current_user_id(request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None

    parts = auth_header.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token = parts[1]

    try:
        payload = decode_access_token(token)
    except Exception:
        return None

    return int(payload["sub"])


async def register(request):
    data = await request.json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return web.json_response(
            {"error": "email and password are required"},
            status=400,
        )

    async with Session() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )

        existing_user = result.scalar_one_or_none()

        if existing_user is not None:
            return web.json_response(
                {"error": "User already exists"},
                status=409,
            )

        user = User(
            email=email,
            password_hash=hash_password(password),
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

    return web.json_response(
        {
            "id": user.id,
            "email": user.email,
        },
        status=201,
    )


async def login(request):
    data = await request.json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return web.json_response(
            {"error": "email and password are required"},
            status=400,
        )

    async with Session() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )

        user = result.scalar_one_or_none()

    if user is None:
        return web.json_response(
            {"error": "Invalid email or password"},
            status=401,
        )

    if not verify_password(password, user.password_hash):
        return web.json_response(
            {"error": "Invalid email or password"},
            status=401,
        )

    token = create_access_token(
        user_id=user.id,
        email=user.email,
    )

    return web.json_response({
        "access_token": token,
        "token_type": "Bearer",
    })