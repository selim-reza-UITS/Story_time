# Cyndi Story Telling - API Endpoints

**Base URL:** `http://10.10.13.22:9900`

**API Version:** `v1`

**Full API Prefix:** `http://10.10.13.22:9900/api/v1/`

---

## 🔐 Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/login/` | Login (returns JWT tokens + user role) | ❌ |

---

## 👨‍🎓 Student APIs (`/api/v1/students/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/students/forgot-password/` | Request password reset OTP | ❌ |
| POST | `/api/v1/students/verify-otp/` | Verify OTP code | ❌ |
| POST | `/api/v1/students/reset-password/` | Reset password with OTP | ❌ |
| GET | `/api/v1/students/get/terms-and-conditions/` | Get Terms & Conditions | ❌ |
| GET | `/api/v1/students/get/privacy-and-policy/` | Get Privacy Policy | ❌ |
| GET | `/api/v1/students/my-stories/stats/` | Get student's story statistics | ✅ Student |
| GET/PUT/PATCH/DELETE | `/api/v1/students/profile/` | View/Edit/Delete student profile | ✅ Student |

---

## 👩‍🏫 Teacher APIs (`/api/v1/teachers/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/teachers/dashboard/` | Teacher dashboard overview | ✅ Teacher |
| GET | `/api/v1/teachers/all/students/` | List all students | ✅ Teacher |
| POST | `/api/v1/teachers/all/students/` | Create new student | ✅ Teacher |
| GET | `/api/v1/teachers/students/<id>/action/` | Get single student details | ✅ Teacher |
| PUT | `/api/v1/teachers/students/<id>/action/` | Update student | ✅ Teacher |
| DELETE | `/api/v1/teachers/students/<id>/action/` | Delete student | ✅ Teacher |
| GET | `/api/v1/teachers/my-profile/` | Get teacher's own profile | ✅ Teacher |
| PATCH | `/api/v1/teachers/my-profile/` | Update teacher's profile | ✅ Teacher |
| DELETE | `/api/v1/teachers/my-profile/` | Delete teacher account | ✅ Teacher |
| GET | `/api/v1/teachers/get/terms-and-conditions/` | Get Terms & Conditions | ✅ Teacher |
| GET | `/api/v1/teachers/get/privacy-and-policy/` | Get Privacy Policy | ✅ Teacher |

---

## 🛡️ Admin APIs (`/api/v1/site/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/site/overview/` | Admin dashboard overview | ✅ Admin |
| GET | `/api/v1/site/admin/students/` | List all students | ✅ Admin |
| POST | `/api/v1/site/admin/students/` | Create new student | ✅ Admin |
| GET | `/api/v1/site/admin/students/<id>/` | Get single student | ✅ Admin |
| PUT | `/api/v1/site/admin/students/<id>/` | Update student | ✅ Admin |
| DELETE | `/api/v1/site/admin/students/<id>/` | Delete student | ✅ Admin |
| GET | `/api/v1/site/admin/teachers/` | List all teachers | ✅ Admin |
| POST | `/api/v1/site/admin/teachers/` | Create new teacher | ✅ Admin |
| GET | `/api/v1/site/admin/teachers/<id>/` | Get single teacher | ✅ Admin |
| PUT | `/api/v1/site/admin/teachers/<id>/` | Update teacher | ✅ Admin |
| DELETE | `/api/v1/site/admin/teachers/<id>/` | Delete teacher | ✅ Admin |
| GET/POST | `/api/v1/site/config/ai/behavior/` | AI Assistant configuration | ✅ Admin |
| GET/POST | `/api/v1/site/config/platform/` | Platform settings | ✅ Admin |
| GET/POST | `/api/v1/site/config/terms-and-conditions/` | Terms & Conditions (view/edit) | ✅ Admin |
| GET/POST | `/api/v1/site/config/privacy-and-policy/` | Privacy Policy (view/edit) | ✅ Admin |

---

## 📚 Story APIs (`/api/v1/stories/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/stories/library/` | List all stories (filtered by grade) | ✅ |
| GET | `/api/v1/stories/read/<id>/` | Read story with pagination | ✅ |
| GET | `/api/v1/stories/editor/` | Get story editor | ✅ |
| POST | `/api/v1/stories/editor/` | Create new story | ✅ |
| GET | `/api/v1/stories/editor/<id>/` | Get story for editing | ✅ |
| PATCH | `/api/v1/stories/editor/<id>/` | Update story | ✅ |
| DELETE | `/api/v1/stories/editor/<id>/` | Delete story | ✅ |
| POST | `/api/v1/stories/chat/owlbert/` | Chat with Owlbert AI assistant | ✅ |
| POST | `/api/v1/stories/ai/realtime-check/` | Real-time spelling/grammar check | ✅ |
| GET | `/api/v1/stories/continue-reading/` | Get stories in progress | ✅ |

---

## 🔄 User Flow by Role

### Student Flow
1. **Login** → `POST /api/v1/auth/login/`
2. **View Profile** → `GET /api/v1/students/profile/`
3. **Browse Stories** → `GET /api/v1/stories/library/`
4. **Read Story** → `GET /api/v1/stories/read/<id>/`
5. **Continue Reading** → `GET /api/v1/stories/continue-reading/`
6. **Write Story** → `POST /api/v1/stories/editor/`
7. **Chat with Owlbert** → `POST /api/v1/stories/chat/owlbert/`
8. **Get Writing Help** → `POST /api/v1/stories/ai/realtime-check/`
9. **View Stats** → `GET /api/v1/students/my-stories/stats/`

### Teacher Flow
1. **Login** → `POST /api/v1/auth/login/`
2. **View Dashboard** → `GET /api/v1/teachers/dashboard/`
3. **Manage Students** → `GET/POST /api/v1/teachers/all/students/`
4. **View/Edit Student** → `GET/PUT/DELETE /api/v1/teachers/students/<id>/action/`
5. **Manage Profile** → `GET/PATCH/DELETE /api/v1/teachers/my-profile/`

### Admin Flow
1. **Login** → `POST /api/v1/auth/login/`
2. **View Dashboard** → `GET /api/v1/site/overview/`
3. **Manage Students** → `CRUD /api/v1/site/admin/students/`
4. **Manage Teachers** → `CRUD /api/v1/site/admin/teachers/`
5. **Configure AI** → `GET/POST /api/v1/site/config/ai/behavior/`
6. **Platform Settings** → `GET/POST /api/v1/site/config/platform/`
7. **Legal Pages** → `GET/POST /api/v1/site/config/terms-and-conditions/` & `privacy-and-policy/`

---

## 📝 Login Response Structure

```json
{
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "user",
        "is_student": true,
        "is_teacher": false,
        "is_admin_user": false
    }
}
```

Use `is_student`, `is_teacher`, or `is_admin_user` to determine user role and show appropriate UI.
