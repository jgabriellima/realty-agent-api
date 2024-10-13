from fastapi import APIRouter

from api_template.celery import celery_app

router = APIRouter()


def check_celery_status():
    try:
        result = celery_app.control.ping(timeout=1.0)
        if result:
            return {"status": "healthy", "details": result}
        return {"status": "unhealthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@router.get("/")
async def celery_health_check():
    status = check_celery_status()
    return status
