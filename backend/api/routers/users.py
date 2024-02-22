from typing import Tuple

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager
from fastapi_users.authentication import Strategy
from sqlalchemy.future import select
from starlette.requests import Request

from api.conf import Config
from api.database.sqlalchemy import get_async_session_context, get_user_db_context
from api.exceptions import UserNotExistException, AuthenticationFailedException
from api.models.db import User
from api.response import response
from api.schemas import UserRead, UserUpdate, UserCreate, UserUpdateAdmin, UserReadAdmin, UserSettingSchema
from api.users import auth_backend, fastapi_users, current_active_user, get_user_manager_context, current_super_user, \
    get_user_manager, UserManager
from api.database.my_email import send_email
from api.database.my_redis import client
from fastapi_users import exceptions
router = APIRouter()
config = Config()


# router.include_router(
#     fastapi_users.get_auth_router(auth_backend), prefix="/auth", tags=["auth"]
# )


@router.post("/auth/login", name=f"auth:{auth_backend.name}.login")
async def login(
        request: Request,
        credentials: OAuth2PasswordRequestForm = Depends(),
        user_manager: UserManager = Depends(get_user_manager),
        strategy: Strategy[User, int] = Depends(auth_backend.get_strategy),
):
    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        raise AuthenticationFailedException()
    # if requires_verification and not user.is_verified:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=ErrorCode.LOGIN_USER_NOT_VERIFIED,
    #     )
    resp = await auth_backend.login(strategy, user)
    return response(200, headers=resp.headers)


get_current_user_token = fastapi_users.authenticator.current_user_token(
    active=True, verified=False
)


@router.post("/auth/logout", name=f"auth:{auth_backend.name}.logout")
async def logout(
        user_token: Tuple[User, str] = Depends(get_current_user_token),
        strategy: Strategy[User, int] = Depends(auth_backend.get_strategy),
):
    user, token = user_token
    resp = await auth_backend.logout(strategy, user, token)
    return response(200, headers=resp.headers)


@router.post("/auth/register", response_model=UserReadAdmin, tags=["auth"])
async def register(
        request: Request,
        user_create: UserCreate,
        # _user: User = Depends(current_super_user),
):
    """注册时不能指定setting，使用默认setting"""
    async with get_async_session_context() as session:
        async with get_user_db_context(session) as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                # check captcha
                flag = client.exists(user_create.remark.lower())
                if not flag:
                    return response(400, message="验证码错误")
                user = await user_manager.create(user_create, safe=False, request=request)
                welcome_subject = "Bear Baby AI:Welcome to Our Platform!"
                try:
                    await send_email(user.email, welcome_subject, user.username, "0")
                except Exception as e:
                    # 可以选择记录邮件发送失败的错误，但不阻止用户注册流程
                    print(f"Failed to send welcome email: {e}")
                return UserReadAdmin.model_validate(user)


from pydantic import BaseModel, Field, EmailStr


class PasswordResetRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=4, max_length=6, description="The verification code sent to your email.")
    newPassword: str = Field(..., min_length=6, description="Your new password.")


@router.post("/auth/reset_password", response_model=UserReadAdmin, tags=["auth"])
async def reset_password(
        request: Request,
        reset_request: PasswordResetRequest,
):
    """重置密码接口，需要提供邮箱、验证码和新密码"""
    async with get_async_session_context() as session:
        async with get_user_db_context(session) as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                # 验证码校验
                captcha_key = f"captcha:{reset_request.code.lower()}"
                stored_captcha = client.get(captcha_key)
                # if not stored_captcha or stored_captcha != reset_request.code:
                #     raise response(400, "验证码错误或已过期")

                # 寻找用户并重置密码
                try:
                    user = await user_manager.get_by_email(reset_request.email)
                except exceptions.UserNotExists:
                    # 当找不到用户时，返回一个明确的错误响应
                    return response(404, "邮箱不存在")

                # 更新用户密码
                await user_manager.update_password(user, reset_request.new_password)

                # 发送密码重置成功的邮件
                try:
                    success_subject = "Your password has been reset successfully"
                    await send_email(user.email, success_subject, user.username, "1")  # 假设"1"表示密码重置邮件
                except Exception as e:
                    # 记录邮件发送失败的错误，但不阻止流程
                    print(f"Failed to send password reset success email: {e}")

                # 清除验证码
                client.delete(captcha_key)

                return UserReadAdmin.model_validate(user)


@router.get("/user", tags=["user"])
async def get_all_users(_user: User = Depends(current_super_user)):
    async with get_async_session_context() as session:
        r = await session.execute(select(User))
        results = r.scalars().all()
        return results


# router.include_router(
#     fastapi_users.get_users_router(UserRead, UserUpdate),
#     prefix="/user",
#     tags=["user"],
# )


@router.get("/user/me", response_model=UserRead, tags=["user"])
async def get_me(user: User = Depends(current_active_user)):
    user_read = UserRead.model_validate(user)
    for source in ["openai_api", "openai_web"]:
        source_setting = getattr(user_read.setting, source)
        global_enabled_models = getattr(config, source).enabled_models
        available_models = []
        for model in source_setting.available_models:
            if model in global_enabled_models:
                available_models.append(model)
        source_setting.available_models = available_models
        setattr(user_read.setting, source, source_setting)
    if not config.openai_web.enabled:
        user_read.setting.openai_web.allow_to_use = False
    if not config.openai_api.enabled:
        user_read.setting.openai_api.allow_to_use = False
    if config.openai_web.disable_uploading:
        user_read.setting.openai_web.disable_uploading = True
    return user_read


@router.patch("/user/me", response_model=UserRead, tags=["user"])
async def update_me(
        request: Request,
        user_update: UserUpdate,  # type: ignore
        _user: User = Depends(current_active_user),
):
    async with get_async_session_context() as session:
        async with get_user_db_context(session) as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                user = await session.get(User, _user.id)
                user = await user_manager.update(
                    user_update, user, safe=True, request=request
                )
                return UserRead.model_validate(user)


@router.get("/user/{user_id}", response_model=UserReadAdmin, tags=["user"])
async def admin_get_user(user_id: int, _user: User = Depends(current_super_user)):
    async with get_async_session_context() as session:
        user = await session.get(User, user_id)
        if user is None:
            raise UserNotExistException()
        result = UserRead.model_validate(user)
        return result


@router.patch("/user/{user_id}", tags=["user"])
async def admin_update_user(user_update_admin: UserUpdateAdmin, request: Request,
                            user_id: int, _user: User = Depends(current_super_user)):
    async with get_async_session_context() as session:
        async with get_user_db_context(session) as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                user = await session.get(User, user_id)
                user = await user_manager.update(
                    user_update_admin, user, safe=False, request=request
                )
                return UserReadAdmin.model_validate(user)


@router.delete("/user/{user_id}", tags=["user"])
async def admin_delete_user(user_id: int, _user: User = Depends(current_super_user)):
    async with get_async_session_context() as session:
        user = await session.get(User, user_id)
        await session.delete(user)
        await session.commit()
        return None


@router.patch("/user/{user_id}/setting", response_model=UserReadAdmin, tags=["user"])
async def admin_update_user_setting(user_id: int, user_setting: UserSettingSchema,
                                    _user: User = Depends(current_super_user)):
    async with get_async_session_context() as session:
        user = await session.get(User, user_id)
        if user is None:
            raise UserNotExistException()
        for key, value in user_setting.dict(exclude={'id', 'user_id'}).items():
            setattr(user.setting, key, value)
        await session.commit()
        await session.refresh(user)
        return UserReadAdmin.model_validate(user)
