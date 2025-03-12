# Strava Integration API

API backend cho ứng dụng tích hợp với Strava, cho phép người dùng đăng ký, đăng nhập, và kết nối với tài khoản Strava để lấy dữ liệu hoạt động thể thao.

## Tính năng chính
- Đăng ký, đăng nhập, đăng xuất tài khoản
- Xác nhận tài khoản qua email
- Kết nối với Strava API để lấy dữ liệu hoạt động
- Lấy và hiển thị các hoạt động trong ngày
- Bảo mật với JWT authentication

## Yêu cầu hệ thống
- Python 3.8+
- FastAPI
- SQLite3
- Các thư viện Python được liệt kê trong `requirements.txt`
- Tài khoản Strava và thông tin ứng dụng từ Strava API

## Cài đặt

### Clone repository:
```sh
git clone https://github.com/yourusername/strava-integration.git
cd strava-integration
```

### Tạo và kích hoạt môi trường ảo:
```sh
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### Cài đặt các thư viện:
```sh
pip install -r requirements.txt
```

### Tạo file `.env` với nội dung:
```
SECRET_KEY=your_secret_key_change_this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

EMAIL_FROM=your-email@example.com
EMAIL_USERNAME=your-email@example.com
EMAIL_PASSWORD=your-email-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

STRAVA_CLIENT_ID=your_strava_client_id
STRAVA_CLIENT_SECRET=your_strava_client_secret
STRAVA_REDIRECT_URI=http://localhost:8000/strava/callback
```

### Chạy ứng dụng:
```sh
uvicorn app.main:app --reload
```

## Cấu trúc dự án
```
strava_backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # Điểm khởi đầu ứng dụng
│   ├── config.py                # Cấu hình ứng dụng
│   ├── database.py              # Kết nối và mô hình DB
│   ├── models/                  # Các mô hình dữ liệu
│   │   ├── __init__.py
│   │   ├── user.py              # Mô hình người dùng
│   │   └── activity.py          # Mô hình hoạt động
│   ├── routes/                  # Các endpoint API
│   │   ├── __init__.py
│   │   ├── auth.py              # Xác thực người dùng
│   │   ├── strava.py            # Kết nối Strava
│   │   └── activities.py        # Quản lý hoạt động
│   ├── services/                # Logic nghiệp vụ
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Xử lý xác thực
│   │   ├── email_service.py     # Gửi email
│   │   └── strava_service.py    # Tương tác với Strava API
│   └── utils/                   # Các tiện ích
│       ├── __init__.py
│       ├── security.py          # Bảo mật, JWT
│       └── helpers.py           # Hàm hỗ trợ
│
├── tests/                       # Kiểm thử đơn vị
├── .env                         # Biến môi trường
├── requirements.txt             # Các thư viện cần thiết
└── README.md                    # Hướng dẫn
```

## API Endpoints

### Authentication
- `POST /auth/register` - Đăng ký tài khoản mới
- `POST /auth/verify-email` - Xác nhận email
- `POST /auth/login` - Đăng nhập
- `POST /auth/logout` - Đăng xuất

### Strava Integration
- `GET /strava/authorize` - Lấy URL ủy quyền Strava
- `GET /strava/callback` - Xử lý callback từ Strava (chuyển hướng)
- `POST /strava/callback` - Xử lý mã ủy quyền để lấy token
- `DELETE /strava/disconnect` - Ngắt kết nối tài khoản Strava

### Activities
- `GET /activities/today` - Lấy các hoạt động trong ngày
- `GET /activities/{activity_id}` - Lấy chi tiết một hoạt động

## Hướng dẫn sử dụng

### 1. Đăng ký tài khoản
```sh
POST /auth/register
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "SecurePass456"
}
```

### 2. Đăng nhập
```sh
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=newuser&password=SecurePass456
```

### 3. Kết nối với Strava
#### a. Lấy URL ủy quyền:
```sh
GET /strava/authorize
Authorization: Bearer your_access_token
```

#### b. Mở URL trong trình duyệt và ủy quyền với Strava
#### c. Sao chép mã ủy quyền từ trang callback
#### d. Gửi mã ủy quyền:
```sh
POST /strava/callback
Authorization: Bearer your_access_token
Content-Type: application/json

{
  "code": "your_strava_authorization_code"
}
```

### 4. Lấy hoạt động trong ngày
```sh
GET /activities/today
Authorization: Bearer your_access_token
```

### 5. Đăng xuất
```sh
POST /auth/logout
Authorization: Bearer your_access_token
```

