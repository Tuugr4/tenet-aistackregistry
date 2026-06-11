from app.routers.applications import router as applications_router
from app.routers.resources import resource_routers

all_routers = [applications_router, *resource_routers]
