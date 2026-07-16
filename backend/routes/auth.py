"""
Authentication API routes.
Provides login, token refresh, and user info endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from backend.models.schemas import LoginRequest, TokenResponse
from backend.services.auth import create_access_token, get_current_user
from backend.services.container import get_auth_service, get_container, AppContainer

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, container: AppContainer = Depends(get_container)):
    auth_service = container.auth_service
    user = await auth_service.authenticate(request.username, request.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )
    token = create_access_token(user["username"], user["role"])
    return {"access_token": token}


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user.get("sub", "unknown"),
        "role": current_user.get("role", "analyst"),
    }
