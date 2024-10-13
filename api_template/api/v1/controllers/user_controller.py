import logging

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from api_template.api.common.errors import APIError
from api_template.api.common.pagination import Page, Paginator, paginate
from api_template.api.v1.auth.auth import get_current_active_user, require_auth
from api_template.api.v1.dependencies import get_db
from api_template.api.v1.schemas.user_schemas import UserCreate, UserResponse, UserUpdate
from api_template.api.v1.services.user_service import UserService
from api_template.celery.tasks.general_tasks import example_task
from api_template.db.models.user import User
from api_template.queue.core.manager.queue_manager import queue_manager

router = APIRouter(prefix="/users")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

logger = logging.getLogger(__name__)


def get_user_service(db=Depends(get_db)):
    return UserService(db)


@router.post("/", response_model=UserResponse, status_code=201)
@require_auth
async def create_user(
    user: UserCreate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Create a new user.

    This endpoint allows creating a new user with the provided information.
    Only authenticated users can create new users.
    """
    try:
        return await user_service.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{user_id}", response_model=UserUpdate)
async def update_user(
    user_id: int,
    user: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Update an existing user.

    This endpoint allows updating the information of an existing user.
    Only authenticated users can update user information.
    """
    updated_user = await user_service.update_user(user_id, user)
    if updated_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


@router.delete("/{user_id}", response_model=bool)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    Delete a user.

    This endpoint allows deleting an existing user.
    Only authenticated users can delete users.
    """
    result = await user_service.delete_user(user_id)
    if not result:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    return result


@router.get("/", response_model=Page[UserResponse])
async def list_users(
    paginator: Paginator = Depends(), user_service: UserService = Depends(get_user_service)
):
    """
    List users.

    This endpoint returns a paginated list of users.
    Only authenticated users can list users.
    """
    users, total = await user_service.get_users(
        skip=(paginator.page - 1) * paginator.size, limit=paginator.size
    )
    return paginate(users, paginator, total)


@router.get("/test-queue", response_model=dict)
async def test_queue(message: str, request: Request):
    channel = "user_channel"
    publisher = queue_manager.get_publisher("user_channel")

    if not publisher:
        raise APIError(
            status_code=400, detail=f"Publisher for '{channel}' not found in application state"
        )

    logger.info(f"Sending message to queue: {message}")
    await publisher.publish_message("user_channel", {"type": "test_message", "content": message})

    return {"status": "Message sent to queue successfully"}


@router.get("/test-task-without-result", response_model=dict)
async def test_task_without_result(message: str, request: Request):
    task_id = example_task.delay(message)
    return {"status": f"Message sent to queue successfully: {task_id}"}


@router.get("/test-task-with-result", response_model=dict)
async def test_task_with_result(message: str, request: Request):
    task_id = example_task.delay(message)
    result = AsyncResult(task_id.id)
    return {"status": f"Message sent to queue successfully: {task_id.id}", "result": result.get()}
