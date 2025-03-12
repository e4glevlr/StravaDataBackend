from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import auth_service, strava_service
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/strava", tags=["Strava Integration"])


class StravaAuthResponse(BaseModel):
    code: str


@router.get("/authorize")
async def authorize_strava(current_user: User = Depends(auth_service.get_current_user)):
    """Trả về URL để người dùng ủy quyền với Strava"""
    auth_url = strava_service.get_authorization_url()
    return {"authorization_url": auth_url}


@router.get("/callback")
async def strava_callback_get(
        code: str = Query(...),
        state: str = Query(None),
        scope: str = Query(None),
        request: Request = None
):
    """Xử lý callback GET từ Strava sau khi người dùng ủy quyền

    Endpoint này sẽ hiển thị một trang HTML với mã ủy quyền để người dùng có thể sao chép
    và sử dụng trong ứng dụng của họ.
    """
    # Tạo HTML response để hiển thị mã ủy quyền cho người dùng
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Strava Authorization Successful</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .code-box {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .code {{ font-family: monospace; word-break: break-all; }}
            button {{ background-color: #4CAF50; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }}
            button:hover {{ background-color: #45a049; }}
        </style>
    </head>
    <body>
        <h1>Strava Authorization Successful!</h1>
        <p>Your authorization code is:</p>
        <div class="code-box">
            <p class="code" id="auth-code">{code}</p>
        </div>
        <button onclick="copyCode()">Copy Code</button>
        <p>Please copy this code and use it in your application to complete the authorization process.</p>

        <script>
            function copyCode() {{
                const codeElement = document.getElementById('auth-code');
                const textArea = document.createElement('textarea');
                textArea.value = codeElement.textContent;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('Code copied to clipboard!');
            }}
        </script>
    </body>
    </html>
    """

    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)


@router.post("/callback")
async def strava_callback_post(
        auth_response: StravaAuthResponse,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """Xử lý callback POST từ ứng dụng sau khi người dùng ủy quyền"""
    try:
        tokens = await strava_service.exchange_code_for_token(auth_response.code)

        # Lưu token vào DB
        current_user.strava_access_token = tokens["access_token"]
        current_user.strava_refresh_token = tokens["refresh_token"]
        current_user.strava_token_expires_at = tokens["expires_at"]
        db.commit()

        return {"message": "Strava account linked successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to link Strava account: {str(e)}")


@router.delete("/disconnect")
async def disconnect_strava(
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """Ngắt kết nối tài khoản Strava"""
    if not current_user.strava_access_token:
        raise HTTPException(status_code=400, detail="No Strava account linked")

    try:
        await strava_service.deauthorize(current_user.strava_access_token)

        # Xóa thông tin token
        current_user.strava_access_token = None
        current_user.strava_refresh_token = None
        current_user.strava_token_expires_at = None
        db.commit()

        return {"message": "Strava account disconnected successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to disconnect Strava account: {str(e)}")