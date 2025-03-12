# app/services/strava_service.py
import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.config import settings
from app.models.user import User
import time


def get_authorization_url():
    """Tạo URL ủy quyền Strava"""
    return (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={settings.STRAVA_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={settings.STRAVA_REDIRECT_URI}"
        f"&approval_prompt=force"
        f"&scope=activity:read_all"
    )


async def exchange_code_for_token(code: str):
    """Đổi mã ủy quyền lấy token truy cập"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": settings.STRAVA_CLIENT_ID,
                "client_secret": settings.STRAVA_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code"
            }
        )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get Strava token")

        return response.json()


async def refresh_token(refresh_token: str):
    """Làm mới token truy cập khi hết hạn"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": settings.STRAVA_CLIENT_ID,
                "client_secret": settings.STRAVA_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }
        )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to refresh Strava token")

        return response.json()


async def check_and_refresh_token(user: User, db: Session):
    """Kiểm tra và làm mới token nếu cần"""
    current_time = int(time.time())

    # Nếu token sắp hết hạn (còn dưới 1 giờ), làm mới nó
    if user.strava_token_expires_at and user.strava_token_expires_at - current_time < 3600:
        tokens = await refresh_token(user.strava_refresh_token)

        user.strava_access_token = tokens["access_token"]
        user.strava_refresh_token = tokens["refresh_token"]
        user.strava_token_expires_at = tokens["expires_at"]
        db.commit()

    return user


async def get_activities(access_token: str, after=None, before=None, page=1, per_page=30):
    """Lấy danh sách hoạt động từ Strava API"""
    params = {"page": page, "per_page": per_page}

    if after:
        params["after"] = after
    if before:
        params["before"] = before

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.strava.com/api/v3/athlete/activities",
            params=params,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch activities from Strava")

        return response.json()


async def deauthorize(access_token: str):
    """Hủy quyền truy cập Strava"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://www.strava.com/oauth/deauthorize",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to deauthorize Strava access")

        return response.json()