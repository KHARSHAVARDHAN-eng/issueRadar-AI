import logging
import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.db import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    encrypt_token,
    verify_refresh_token,
)
from app.models.user import User
from app.schemas.user import UserRead

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/login")
async def github_login():
    """Redirect client to GitHub OAuth authorization screen."""
    state = secrets.token_urlsafe(16)
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": "user:email read:user",
        "state": state,
    }
    github_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    response = RedirectResponse(url=github_url)
    # Store CSRF state token in cookie (expires in 10 minutes)
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        max_age=600,
        samesite="lax",
    )
    return response


@router.get("/callback")
async def github_callback(
    code: str = Query(..., description="Authorization code from GitHub"),
    state: str | None = Query(None, description="CSRF state string"),
    db: AsyncSession = Depends(get_db),
):
    """Handle GitHub OAuth redirect callback, exchange code for token,
    upsert user, set session cookie.
    """
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code",
        )

    # 1. Exchange code for GitHub access token
    async with httpx.AsyncClient(timeout=10.0) as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GITHUB_REDIRECT_URI,
            },
        )

        if token_response.status_code != 200:
            logger.error(f"GitHub token exchange failed: {token_response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code with GitHub",
            )

        token_data = token_response.json()
        github_token = token_data.get("access_token")

        if not github_token:
            error_desc = token_data.get("error_description", "Invalid response from GitHub")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"GitHub OAuth error: {error_desc}",
            )

        # 2. Fetch user profile from GitHub
        user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/json",
            },
        )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user profile from GitHub",
            )

        profile = user_response.json()
        github_id = profile.get("id")
        username = profile.get("login")
        avatar_url = profile.get("avatar_url")
        email = profile.get("email")

        # 3. If primary email is missing from profile, fetch email list
        if not email:
            email_response = await client.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {github_token}",
                    "Accept": "application/json",
                },
            )
            if email_response.status_code == 200:
                emails = email_response.json()
                for em in emails:
                    if em.get("primary") and em.get("verified"):
                        email = em.get("email")
                        break
                if not email and emails:
                    email = emails[0].get("email")

        if not github_id or not username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incomplete GitHub user profile returned",
            )

        # 4. Encrypt GitHub access token before database storage
        encrypted_token = encrypt_token(github_token)

        # 5. Create or update user in database
        result = await db.execute(select(User).where(User.github_id == github_id))
        user = result.scalar_one_or_none()

        if user:
            user.username = username
            user.avatar_url = avatar_url
            user.email = email
            user.encrypted_github_token = encrypted_token
        else:
            user = User(
                github_id=github_id,
                username=username,
                email=email,
                avatar_url=avatar_url,
                encrypted_github_token=encrypted_token,
            )
            db.add(user)

        await db.commit()
        await db.refresh(user)

        # 6. Generate JWT session token
        session_token = create_access_token(data={"sub": str(user.id)})

        # 7. Redirect to frontend dashboard with HttpOnly cookie
        redirect_to = f"{settings.FRONTEND_URL}/dashboard"
        response = RedirectResponse(url=redirect_to, status_code=status.HTTP_302_FOUND)

        max_age = settings.JWT_EXPIRE_MINUTES * 60
        response.set_cookie(
            key="access_token",
            value=session_token,
            httponly=True,
            max_age=max_age,
            path="/",
            samesite="lax",
            secure=False,  # Set to True in HTTPS production
        )
        return response


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    """Fetch currently authenticated user details."""
    return current_user


@router.post("/refresh", summary="Rotate JWT access token using refresh token")
async def refresh_token_endpoint(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token") or request.headers.get("X-Refresh-Token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    payload = verify_refresh_token(refresh_token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = payload["sub"]
    new_access_token = create_access_token(data={"sub": user_id})
    new_refresh_token = create_refresh_token(data={"sub": user_id})

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.JWT_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=30 * 24 * 3600,
    )

    return {"message": "Token refreshed successfully", "access_token": new_access_token}


@router.post("/logout")
async def logout(response: Response):
    """Log out user by clearing session cookie."""
    response.delete_cookie(key="access_token", path="/", samesite="lax")
    return {"message": "Logged out successfully"}
