# API Specification

Complete REST API reference for the Personalized Adaptive Typing Trainer.

---

## 📡 Base URL

```
http://localhost:8000/api/v1
```

All responses are JSON. Errors follow this format:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

---

## 🔐 Authentication

All protected endpoints require a bearer token:

```
Authorization: Bearer <access_token>
```

Tokens are obtained via `/auth/login` or `/auth/register`.

---

## 🚪 Auth Endpoints

### Register User

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": { ... }
}
```

### Refresh Token

```http
POST /auth/refresh
Authorization: Bearer <current_token>
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Logout

```http
POST /auth/logout
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

---

## 📝 Session Endpoints

### Create Session

```http
POST /sessions
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "test_type": "standard",
  "difficulty_level": 2,
  "custom_text": null,
  "adapter_config": {
    "focus_mode": true
  }
}
```

**Response** (201 Created):
```json
{
  "id": 42,
  "user_id": 1,
  "test_type": "standard",
  "difficulty_level": 2,
  "metrics": {
    "wpm": 0,
    "accuracy": 0,
    "errors": 0,
    "key_presses": 0
  },
  "status": "in_progress",
  "started_at": "2024-01-15T10:35:00Z",
  "ended_at": null,
  "created_at": "2024-01-15T10:35:00Z"
}
```

### Get Session

```http
GET /sessions/{session_id}
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": 42,
  "user_id": 1,
  "test_type": "standard",
  "difficulty_level": 2,
  "metrics": {
    "wpm": 65.5,
    "accuracy": 94.2,
    "errors": 3,
    "key_presses": 325
  },
  "status": "completed",
  "started_at": "2024-01-15T10:35:00Z",
  "ended_at": "2024-01-15T10:40:00Z",
  "created_at": "2024-01-15T10:35:00Z"
}
```

### List Sessions

```http
GET /sessions?skip=0&limit=20
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
[
  {
    "id": 42,
    "user_id": 1,
    ...
  },
  {
    "id": 41,
    "user_id": 1,
    ...
  }
]
```

### Update Session (Real-time Metrics)

```http
PUT /sessions/{session_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "metrics": {
    "wpm": 65.5,
    "accuracy": 94.2,
    "errors": 3,
    "key_presses": 325
  },
  "status": "completed",
  "end_time": "2024-01-15T10:40:00Z"
}
```

**Response** (200 OK):
```json
{
  "id": 42,
  ...
}
```

### Delete Session

```http
DELETE /sessions/{session_id}
Authorization: Bearer <access_token>
```

**Response** (204 No Content):
```
(empty)
```

---

## 👤 User Endpoints

### Get Current User

```http
GET /users/me
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Public User Profile

```http
GET /users/{user_id}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "username": "john_doe",
  "full_name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Update Profile

```http
PUT /users/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "John Updated",
  "preferences": { ... }
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  ...
}
```

### Get Preferences

```http
GET /users/preferences
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "theme": "dark",
  "notifications_enabled": true,
  "language": "en",
  "keyboard_layout": "qwerty",
  "sound_enabled": true,
  "difficulty_auto_adjust": true
}
```

### Set Preferences

```http
POST /users/preferences
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "theme": "dark",
  "notifications_enabled": false,
  "language": "es"
}
```

**Response** (200 OK):
```json
{
  "theme": "dark",
  ...
}
```

---

## 📊 Analytics Endpoints

### Get User Statistics

```http
GET /analytics/stats?days=30
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "total_sessions": 15,
  "avg_wpm": 58.3,
  "avg_accuracy": 91.2,
  "best_wpm": 72.5,
  "total_errors": 45,
  "improvement_trend": 8.5
}
```

### Get Progress Data

```http
GET /analytics/progress?days=30
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
[
  {
    "date": "2024-01-01T00:00:00Z",
    "wpm": 55.0,
    "accuracy": 89.5
  },
  {
    "date": "2024-01-02T00:00:00Z",
    "wpm": 58.2,
    "accuracy": 91.0
  },
  ...
]
```

### Get Strengths & Weaknesses

```http
GET /analytics/strengths-weaknesses
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "strongest_keys": ["e", "t", "a", "o", "i"],
  "weakest_keys": ["q", "z", "x", "colon", "semicolon"],
  "common_error_patterns": [
    {
      "pattern": "Shift key combinations",
      "frequency": 0.12
    }
  ]
}
```

### Get Leaderboard

```http
GET /analytics/leaderboard?limit=10&timeframe=all_time
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
[
  {
    "rank": 1,
    "user_id": 5,
    "username": "speed_demon",
    "best_wpm": 145.3,
    "avg_accuracy": 97.8,
    "total_sessions": 250
  },
  {
    "rank": 2,
    "user_id": 3,
    "username": "type_master",
    "best_wpm": 138.7,
    "avg_accuracy": 96.2,
    "total_sessions": 180
  }
]
```

### Get User Rank

```http
GET /analytics/user-rank
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "current_rank": 47,
  "percentile": 85.3,
  "wpm_needed_for_next_rank": 3.5,
  "nearby_ranks": [
    { "rank": 46, "username": "typist_pro", "best_wpm": 95.2 },
    { "rank": 47, "username": "you", "best_wpm": 91.7 },
    { "rank": 48, "username": "speedrunner", "best_wpm": 89.3 }
  ]
}
```

---

## 🔧 Adapter Endpoints

### Get Adapter Configuration

```http
GET /adapter/config
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "adapter_type": "rule_based",
  "parameters": {
    "accuracy_threshold": 85,
    "wpm_threshold": 40,
    "error_threshold": 5,
    "improvement_rate": 2
  }
}
```

### Update Adapter Configuration

```http
PUT /adapter/config
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "adapter_type": "rule_based",
  "parameters": {
    "accuracy_threshold": 90,
    "wpm_threshold": 45
  }
}
```

**Response** (200 OK):
```json
{
  "adapter_type": "rule_based",
  "parameters": { ... }
}
```

### Get Recommendation

```http
POST /adapter/recommend
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "session_id": 42
}
```

**Response** (200 OK):
```json
{
  "next_difficulty": 4,
  "focus_areas": [
    "Shift key combinations",
    "Number row accuracy"
  ],
  "reason": "Excellent performance in last 2 sessions. Ready for increased difficulty.",
  "confidence": 0.87
}
```

### List Available Adapters

```http
GET /adapter/available-adapters
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
[
  {
    "id": "rule_based",
    "name": "Rule-Based Adapter",
    "description": "Uses configurable thresholds for difficulty recommendations",
    "version": "1.0.0"
  },
  {
    "id": "ml",
    "name": "Machine Learning Adapter",
    "description": "AI-powered predictions based on user patterns (requires model training)",
    "version": "0.1.0"
  }
]
```

---

## ✅ Health Endpoints

### Health Check

```http
GET /
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "app": "Personalized Adaptive Typing Trainer",
  "version": "0.1.0",
  "adapter": "rule_based"
}
```

### Detailed Health

```http
GET /health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "database": "connected",
  "features": {
    "real_time_feedback": true,
    "analytics": true,
    "leaderboard": true
  }
}
```

---

## ❌ Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data",
  "status_code": 400
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated",
  "status_code": 401
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized to perform this action",
  "status_code": 403
}
```

### 404 Not Found
```json
{
  "detail": "Session not found",
  "status_code": 404
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error"
    }
  ],
  "status_code": 422
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "status_code": 500
}
```

---

## 📚 Interactive Documentation

Once server is running:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## 🔄 Pagination

List endpoints support pagination:

```
GET /sessions?skip=20&limit=10
```

- `skip`: Number of items to skip (default: 0)
- `limit`: Number of items to return (default: 20, max: 100)

---

## ⏱️ Rate Limiting

Coming in Phase 2:
- Rate limit: 100 requests per minute per user
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

---

## 🧪 Example Usage

### Complete Typing Test Flow

```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}'

# Response: { "access_token": "...", ... }

# 2. Create session
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"test_type":"standard","difficulty_level":2}'

# Response: { "id": 42, ... }

# 3. Update metrics (real-time)
curl -X PUT http://localhost:8000/api/v1/sessions/42 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "metrics": {"wpm": 65.5, "accuracy": 94.2, "errors": 3, "key_presses": 325},
    "status": "completed"
  }'

# 4. Get recommendation
curl -X POST http://localhost:8000/api/v1/adapter/recommend \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"session_id": 42}'

# Response: { "next_difficulty": 3, "focus_areas": [...], ... }

# 5. View stats
curl -X GET "http://localhost:8000/api/v1/analytics/stats?days=30" \
  -H "Authorization: Bearer <token>"
```

---

This API is designed to be **intuitive, extensible, and production-ready**. 🚀
