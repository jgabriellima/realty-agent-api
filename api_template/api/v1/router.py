from fastapi import APIRouter

from api_template.config.versioning import APIVersion

from .controllers import user_controller, websearch_controller

router = APIRouter(prefix=f"/api/{APIVersion.V1}")

router.include_router(user_controller.router, tags=["Users"])
router.include_router(websearch_controller.router, tags=["WebSearch"])
