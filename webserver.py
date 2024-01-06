import json

from aiohttp import web
import aioredis

async def main_page(request):
    raise web.HTTPFound('/index.html')

async def index(request):
    return web.FileResponse('/app/index.html')

async def stats_handle(request):
    name = request.match_info.get('stat_name')
    print(name)
    redis = aioredis.from_url("redis://redis:6379")
    data = await redis.get(name)
    if data is None or data == '':
        raise web.HTTPNotFound()
    print(data)
    json_data = json.loads(data)
    return web.json_response(json_data)

app = web.Application()
app.add_routes([web.get('/', main_page),
                web.get('/index.html', index),
                web.static('/css', '/app/css', append_version=True),
                web.static('/js', '/app/js', append_version=True),
                web.get('/stats/{stat_name}', stats_handle)])

if __name__ == '__main__':
    web.run_app(app, port=8080)
