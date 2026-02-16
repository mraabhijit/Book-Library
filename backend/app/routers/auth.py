from typing import Annotated

from fastapi import Depends
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from app import models
from app.schemas import StaffCreate, StaffResponse, Token
from app.utils import oauth2_scheme
from app.services import AuthService

router = APIRouter()


@router.post("/register", response_model=StaffResponse)
async def create_staff(
    staff: StaffCreate,
    service: Annotated[AuthService, Depends(AuthService)],
):
    return await service.register_staff(staff)


@router.get("/me", response_model=StaffResponse)
async def get_current_user_route(
    token: Annotated[str, Depends(oauth2_scheme)],
    service: Annotated[AuthService, Depends(AuthService)],
):
    return await service.get_current_user(token)


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[AuthService, Depends(AuthService)],
):
    return await service.login(form_data.username, form_data.password)


async def get_current_user_dependency(
    token: Annotated[str, Depends(oauth2_scheme)],
    service: Annotated[AuthService, Depends(AuthService)],
) -> models.Staff:
    return await service.get_current_user(token)


CurrentUser = Annotated[models.Staff, Depends(get_current_user_dependency)]
