from aiohttp import web

from app.handlers import (
    create_ad,
    delete_ad,
    get_ad,
    get_ads,
    login,
    register,
    update_ad,
)


async def hello(request):
    return web.json_response({
        "message": "Aiohttp API работает"
    })


app = web.Application()

app.router.add_get("/", hello)
app.router.add_post("/ads", create_ad)
app.router.add_get("/ads", get_ads)
app.router.add_get("/ads/{ad_id}", get_ad)
app.router.add_patch("/ads/{ad_id}", update_ad)
app.router.add_delete("/ads/{ad_id}", delete_ad)
app.router.add_post("/auth/register", register)
app.router.add_post("/auth/login", login)


if __name__ == "__main__":
    web.run_app(app, port=8000)