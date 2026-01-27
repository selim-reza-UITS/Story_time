# Frontend API Integration Guide

**Base URL:** `http://10.10.13.22:9900/api/v1`

---

## 🔐 1. Authentication (All Roles)

### Login
**Endpoint:** `POST /auth/login/`
**Request Body:**
```json
{
  "email": "student@example.com",
  "password": "password123"
}
```
**Response:**
Save `access` token. Check `is_student`, `is_teacher`, `is_admin_user` to route user.
```json
{
  "access": "eyJ0eX...",
  "refresh": "eyJ0eX...",
  "user": {
    "id": 1,
    "email": "student@example.com",
    "is_student": true,
    "is_teacher": false,
    "is_admin_user": false
  }
}
```

---

## 🎓 2. Student Flow

### A. Dashboard (Home)
#### Student Home Data
**Endpoint:** `GET /students/home/`
**Response:**
```json
{
    "unfinished_story_list": [
        {
            "id": 1, 
            "story": { "id": 5, "title": "Dragon" },
            "completion_percentage": 50.0
        }
    ],
    "finished_story_list": [],
    "vocabulary_list": { "apple": "A fruit" },
    "stats": {
        "total_book_read": 10,
        "total_new_words_learned": 5,
        "reading_level": "beginner",
        "reading_title": "Word Explorer",
        "next_level_progress": 45.0
    }
}
```

### B. Library & Reading
#### List Library (with Recommendations)
**Endpoint:** `GET /stories/library/`
**Response:**
```json
{
    "library": [ { "id": 1, "title": "Space Adventure", "grade": 3 } ],
    "recommended": [ { "id": 5, "title": "Teacher Pick", "grade": 3 } ]
}
```

#### Read Story (Pagination)
**Endpoint:** `GET /stories/read/<id>/?page=1`
**Response:**
```json
{
  "id": 1,
  "title": "Space Adventure",
  "page_content": "Once upon a time...",
  "current_page": 1,
  "total_pages": 5,
  "has_next": true,
  "has_previous": false
}
```
*Note: Reading the last page automatically marks the story as completed.*

#### Dictionary Helper (Lookup/Save)
**Endpoint:** `POST /stories/dictionary/`
**Body (Lookup):** `{"word": "asteroid", "action": "lookup"}`
**Body (Save):** `{"word": "asteroid", "action": "save"}`
**Response:**
```json
{
  "word": "asteroid",
  "definition": "A small rocky body orbiting the sun.",
  "audio_url": "http://..."
}
```

#### Reading Tips (AI)
**Endpoint:** `GET /stories/tips/`
**Response:** `{"tip": "Try reading this sentence out loud!"}`

### C. Story Editor (Writing)
#### Create Story
**Endpoint:** `POST /stories/editor/`
**Body:** `{"title": "My New Story", "content": "It was a dark night..."}`

#### Update Story (Auto-save)
**Endpoint:** `PATCH /stories/editor/<id>/`
**Body:** `{"content": "It was a dark and stormy night..."}`

#### Owlbert Chat (AI Guide)
**Endpoint:** `POST /stories/chat/owlbert/`
**Body:** `{"message": "I need an idea for a villain", "story_context": "..."}`

#### Realtime Grammar Check
**Endpoint:** `POST /stories/ai/realtime-check/`
**Body:** `{"text": "He runned fast."}`
**Response:** `{"corrected": "He ran fast.", "has_errors": true}`

### D. Profile
#### View Profile
**Endpoint:** `GET /students/profile/`
**Response:** `{"grade_level": 3, "achievement_level": 2, "level_title": "Word Explorer", ...}`

---

## 👩‍🏫 3. Teacher Flow

### A. Dashboard
**Endpoint:** `GET /teachers/dashboard/`

### B. Student Management
#### List All Students
**Endpoint:** `GET /teachers/all/students/`

#### Register New Student
**Endpoint:** `POST /teachers/all/students/`
**Body:**
```json
{
  "email": "timmy@school.com",
  "password": "password123",
  "first_name": "Timmy",
  "last_name": "Turner",
  "grade_level": 3
}
```

#### Recommend Story to Student
**Endpoint:** `POST /teachers/students/<id>/recommend/`
**Body:** `{"story_id": 5}`

#### Student Details
**Endpoint:** `GET /teachers/students/<id>/action/`

### C. Profile
**Endpoint:** `GET /teachers/my-profile/`

---

## 🛡️ 4. Admin Flow

### A. Overview
**Endpoint:** `GET /site/overview/`

### B. User Management
#### List Students (Detailed Stats)
**Endpoint:** `GET /site/admin/students/`
**Response includes:** `dictionary_search_count`, `story_read_count`.

#### Student Details (Full Stats & Recommendations)
**Endpoint:** `GET /site/admin/students/<id>/`

#### Recommend Story (Admin)
**Endpoint:** `POST /site/admin/students/<id>/recommend/`
**Body:** `{"story_id": 10}`

### C. System Config
#### AI Behavior
**Endpoint:** `POST /site/config/ai/behavior/`
**Body:**
```json
{
  "behavior_instruction": "You are a specialized creative writing assistant for 3rd graders."
}
```

#### Platform Settings
**Endpoint:** `POST /site/config/platform/`
**Body:** `{"platform_name": "Cyndi Stories"}`

#### Terms & Conditions
**Endpoint:** `POST /site/config/terms-and-conditions/`
**Body:** `{"content": "<h1>Terms</h1>..."}`

---

## ℹ️ 5. Public / Shared
**Terms:** `GET /students/get/terms-and-conditions/`
**Privacy:** `GET /students/get/privacy-and-policy/`
