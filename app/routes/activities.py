# app/routes/activities.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from app.database import get_db
from app.services import auth_service, strava_service
from app.models.user import User
from app.models.activity import Activity
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/activities", tags=["Activities"])


class ActivityResponse(BaseModel):
    id: int
    strava_id: str
    name: str
    type: str
    start_date: datetime
    distance: float
    moving_time: int
    elapsed_time: int
    total_elevation_gain: float
    average_speed: float
    max_speed: float

    class Config:
        orm_mode = True


@router.get("/today", response_model=List[ActivityResponse])
async def get_today_activities(
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """Lấy các hoạt động trong ngày hiện tại"""
    if not current_user.strava_access_token:
        raise HTTPException(status_code=400, detail="No Strava account linked")

    # Kiểm tra và làm mới token nếu cần
    current_user = await strava_service.check_and_refresh_token(current_user, db)

    # Lấy hoạt động từ Strava
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    try:
        # Lấy và lưu hoạt động mới từ Strava
        activities = await strava_service.get_activities(
            current_user.strava_access_token,
            after=int(today_start.timestamp())
        )

        # Lưu các hoạt động vào DB nếu chưa tồn tại
        for activity_data in activities:
            existing = db.query(Activity).filter(
                Activity.strava_id == str(activity_data["id"])
            ).first()

            if not existing:
                new_activity = Activity(
                    strava_id=str(activity_data["id"]),
                    user_id=current_user.id,
                    name=activity_data["name"],
                    type=activity_data["type"],
                    start_date=datetime.fromisoformat(activity_data["start_date"].replace("Z", "+00:00")),
                    distance=activity_data["distance"],
                    moving_time=activity_data["moving_time"],
                    elapsed_time=activity_data["elapsed_time"],
                    total_elevation_gain=activity_data["total_elevation_gain"],
                    average_speed=activity_data["average_speed"],
                    max_speed=activity_data["max_speed"]
                )
                db.add(new_activity)

        db.commit()

        # Truy vấn các hoạt động trong ngày từ DB
        today_activities = db.query(Activity).filter(
            Activity.user_id == current_user.id,
            Activity.start_date >= today_start,
            Activity.start_date <= today_end
        ).all()

        return today_activities
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch activities: {str(e)}")


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity_detail(
        activity_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """Lấy chi tiết của một hoạt động cụ thể"""
    activity = db.query(Activity).filter(
        Activity.id == activity_id,
        Activity.user_id == current_user.id
    ).first()

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    return activity