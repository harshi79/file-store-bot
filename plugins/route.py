from aiohttp import web

routes = web.RouteTableDef()


@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response({"service": "FileStoreBot", "status": "ok", "health": "/healthz"})


@routes.get("/healthz", allow_head=True)
async def health_route_handler(request):
    """Unauthenticated liveness endpoint for Render and UptimeRobot."""
    return web.json_response({"status": "ok"})
