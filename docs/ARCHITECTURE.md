# Personalized Adaptive Typing Trainer
## Complete Architecture Blueprint

A full-stack, ML-ready typing trainer that adapts to user performance in real-time.

---

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                        │
│         Responsive UI with real-time metrics display        │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API (JSON)
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                 API LAYER (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Routes: Auth, Sessions, Users, Analytics, Adapter   │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
    ┌───────────┐ ┌──────────┐ ┌──────────────┐
    │ Adapter   │ │Evaluator │ │ Database ORM │
    │ Engine    │ │(Metrics) │ │ (SQLAlchemy) │
    └───────────┘ └──────────┘ └──────────────┘
        │
    ┌───────────────┬───────────────┐
    ↓               ↓               ↓
┌─────────────┐ ┌──────────┐ ┌──────────────┐
│Rule-Based   │ │ML-Ready  │ │Custom Adapters
│Adapter      │ │Adapter   │ │(Extensible)
└─────────────┘ └──────────┘ └──────────────┘
        │
        └──────────────────────┬──────────────────────┐
                               ↓
                   ┌──────────────────────┐
                   │  SQLite/PostgreSQL   │
                   │  (Persistent Data)   │
                   └──────────────────────┘
```

---

## 📁 Monorepo Structure

```
Personalized Typing App/
├── backend/                          # Python FastAPI server
│   ├── app/
│   │   ├── main.py                  # FastAPI application entry
│   │   ├── config.py                # Configuration management
│   │   ├── api/
│   │   │   ├── routes/              # Endpoint implementations
│   │   │   │   ├── auth.py
│   │   │   │   ├── sessions.py
│   │   │   │   ├── users.py
│   │   │   │   ├── analytics.py
│   │   │   │   └── adapter.py
│   │   │   └── schemas.py           # Pydantic validation models
│   │   ├── core/
│   │   │   ├── adapters/            # Pluggable adaptation engines
│   │   │   │   ├── base.py          # Abstract interface
│   │   │   │   ├── rule_based.py    # Heuristic adapter
│   │   │   │   └── ml_ready.py      # ML stub (future)
│   │   │   └── engine/
│   │   │       └── evaluator.py     # Typing metrics calculator
│   │   ├── db/
│   │   │   ├── database.py          # SQLAlchemy setup
│   │   │   ├── models.py            # Data models
│   │   │   └── migrations/          # Alembic migrations
│   │   └── utils/
│   │       └── logging.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/                         # React + TypeScript
│   ├── src/
│   │   ├── components/
│   │   │   ├── Auth/                # Login, Register
│   │   │   ├── TypingTest/          # Core typing interface
│   │   │   ├── Dashboard/           # Stats & progress
│   │   │   ├── Adaptive/            # Difficulty controls
│   │   │   └── Common/              # Layout components
│   │   ├── pages/                   # Route pages
│   │   ├── hooks/                   # Zustand state management
│   │   ├── services/
│   │   │   ├── api.ts               # HTTP client
│   │   │   ├── storage.ts           # LocalStorage utils
│   │   │   └── adapter.ts           # Adapter logic
│   │   ├── types/                   # TypeScript definitions
│   │   └── styles/                  # Tailwind + CSS
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── README.md
│
├── shared/                          # Shared types & constants
│   ├── constants.py
│   └── types.py
│
├── docs/                            # Architecture documentation
│   ├── ARCHITECTURE.md              # This file
│   ├── DATABASE_SCHEMA.md
│   ├── API_SPEC.md
│   └── ADAPTER_SYSTEM.md
│
├── docker-compose.yml               # Local dev environment
├── .gitignore
└── README.md
```

---

## 🔌 Adapter System (The Heart)

The application's genius lies in its **pluggable adapter architecture**—completely decoupled from business logic.

### Base Adapter Interface

All adapters implement `BaseAdapter`:

```python
class BaseAdapter(ABC):
    @abstractmethod
    def get_initial_difficulty(user_profile: dict) -> int
    
    @abstractmethod
    def analyze_session(session_data: dict) -> dict
    
    @abstractmethod
    def recommend_next_difficulty(
        user_history: List[dict],
        current_performance: dict
    ) -> AdapterRecommendation
    
    @abstractmethod
    def get_real_time_feedback(current_stats: dict) -> Optional[str]
```

### Included Adapters

**1. Rule-Based Adapter** (`rule_based.py`)
- Uses configurable thresholds
- Deterministic, explainable decisions
- Perfect for MVP and rule-driven systems
- Config: `accuracy_threshold`, `wpm_threshold`, `improvement_rate`

**2. ML-Ready Adapter** (`ml_ready.py`)
- Inherits from rule-based for immediate functionality
- Prepared for sklearn/TensorFlow integration
- Plugs in ML models without changing API
- Stub methods ready for implementation

### How to Swap Adapters

```env
# .env file
ADAPTER_TYPE=rule_based  # Switch to "ml" for ML adapter
```

Or dynamically via API:
```typescript
await adapterService.updateConfig({ adapter_type: 'ml' })
```

### Extending with Custom Adapters

Create your own:

```python
from app.core.adapters.base import BaseAdapter

class CustomAdapter(BaseAdapter):
    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
    
    # Implement abstract methods...
```

Register in config/factory and switch at runtime.

---

## 💾 Database Schema

### Core Tables

**Users**
```python
- id (Primary Key)
- email (Unique)
- username (Unique)
- hashed_password
- full_name
- is_active
- created_at, updated_at
```

**TypingSessions** (The beating heart)
```python
- id
- user_id (Foreign Key)
- test_type (standard, coding, custom)
- difficulty_level (1-10)
- status (in_progress, completed, paused)
- text_prompt, text_typed
- started_at, ended_at, duration_seconds
- wpm, accuracy, errors, key_presses
- error_details (JSON) - {position: {expected, actual}}
- key_stats (JSON) - Per-key error analysis
- adapter_used (Which adapter made the recommendation)
- adapter_recommendation (JSON) - The recommendation itself
```

**SessionMetrics** (Real-time snapshots)
```python
- id
- session_id
- timestamp
- current_wpm, current_accuracy
- adapter_state (JSON) - Adapter state at this moment
```

**UserAdapterConfig**
```python
- user_id
- adapter_type
- parameters (JSON) - Adapter-specific config
- custom_rules (JSON) - Custom rules for rule-based
```

**UserPreference**
```python
- user_id
- theme, notifications_enabled, language
- keyboard_layout, sound_enabled
- difficulty_auto_adjust
- extra_settings (JSON) - Extensible
```

**UserStatSnapshot** (Pre-computed for fast analytics)
```python
- user_id
- total_sessions, avg_wpm, best_wpm, avg_accuracy
- weekly_improvement, monthly_improvement
- rank, percentile
- period_start, period_end
```

---

## 🔌 API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /register` - Create user
- `POST /login` - Get JWT token
- `POST /refresh` - Refresh token
- `POST /logout` - Invalidate token

### Sessions (`/api/v1/sessions`)
- `POST /` - Create new typing session
- `GET /{id}` - Get session details
- `GET /` - List user's sessions (paginated)
- `PUT /{id}` - Update metrics (real-time)
- `DELETE /{id}` - Delete session

### Users (`/api/v1/users`)
- `GET /me` - Current user profile
- `PUT /me` - Update profile
- `GET /{id}` - Public user profile
- `GET /preferences` - User settings
- `POST /preferences` - Update settings

### Analytics (`/api/v1/analytics`)
- `GET /stats` - User statistics (aggregated)
- `GET /progress` - Time-series progress data
- `GET /strengths-weaknesses` - Performance analysis
- `GET /leaderboard` - Global rankings
- `GET /user-rank` - User's rank position

### Adapter (`/api/v1/adapter`)
- `GET /config` - Current adapter settings
- `PUT /config` - Change adapter config
- `POST /recommend` - Get difficulty recommendation
- `GET /available-adapters` - List installed adapters

---

## 🎨 Frontend Architecture

### State Management (Zustand Stores)

**useAuth**
- `user`, `isAuthenticated`, `isLoading`, `error`
- Methods: `register()`, `login()`, `logout()`, `checkAuth()`

**useTyping**
- Core typing test state
- `currentSession`, `testText`, `typedText`, `isRunning`
- Real-time `realTimeWpm`, `realTimeAccuracy`
- Methods: `startTest()`, `stopTest()`, `addCharacter()`, `calculateMetrics()`

**useSession**
- Session history and management
- Methods: `fetchSessions()`, `createSession()`, `updateSession()`

**useAdapter**
- Adapter configuration
- `currentDifficulty`, `adapterType`, `recommendation`
- Methods: `getRecommendation()`, `updateDifficulty()`, `setAdapterType()`

### Key Services

**API Client** (`services/api.ts`)
- Centralized Axios instance with auth interceptors
- Auto-refreshes tokens on 401
- All backend endpoints wrapped

**Storage Service** (`services/storage.ts`)
- LocalStorage utilities
- Token and user data persistence

**Adapter Service** (`services/adapter.ts`)
- Client-side adapter logic
- Difficulty calculation
- Focus area detection

### Component Structure

```
App.tsx (Router)
├── Header (Logo, nav)
├── Navbar (Secondary nav)
├── Routes
│   ├── / (Home)
│   ├── /login (Public)
│   ├── /register (Public)
│   ├── /typing-test (Protected)
│   ├── /dashboard (Protected)
│   └── /settings (Protected)
└── Footer
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- SQLite (or PostgreSQL)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m app.main
```

Server runs on `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

App runs on `http://localhost:5173`

### Docker (Optional)

```bash
docker-compose up
```

---

## 🧠 Design Principles

### 1. **No Hard Limits**
- Difficulty: 1-10 (easily extended)
- Adapters: Pluggable, swappable
- Database: From SQLite → PostgreSQL seamlessly
- Metrics: JSON fields for extensibility

### 2. **Separation of Concerns**
- **API Layer**: HTTP contracts only
- **Core Layer**: Pure business logic
- **Data Layer**: ORM abstraction
- **Adapter Layer**: Isolated from business logic

### 3. **Future-Ready for ML**
- `MLAdapter` stub ready for sklearn/TensorFlow
- Session data captures everything needed for analysis
- `key_stats` and `error_details` JSON for feature engineering
- Adapter interface supports arbitrary parameters

### 4. **Real-Time Reactive**
- `SessionMetric` table captures granular updates
- `adapter_state` field for stateful adapters
- Real-time feedback channel (HTTP polling or WebSocket ready)

### 5. **Type Safety**
- TypeScript frontend with strict mode
- Pydantic validation on backend
- Shared type definitions

---

## 📊 Data Flow Example: Typing Session

```
User clicks "Start Test"
    ↓
Frontend creates TypingSession (POST /sessions)
    ↓
Backend initializes session, calls adapter.get_initial_difficulty()
    ↓
User types characters
    ↓
Frontend sends metrics updates in real-time (PUT /sessions/{id})
    ↓
Backend calculates metrics, calls adapter.get_real_time_feedback()
    ↓
Backend returns feedback + current metrics
    ↓
Frontend displays updated WPM, accuracy, real-time feedback
    ↓
User completes test
    ↓
Frontend calculates final metrics, calls adapter.recommend_next_difficulty()
    ↓
Backend stores recommendation, returns difficulty suggestion
    ↓
Frontend displays results + recommendation for next session
```

---

## 🔐 Security Considerations

- ✅ JWT authentication with HS256
- ✅ Password hashing (bcrypt via passlib)
- ✅ CORS configured for frontend
- ✅ Request/response validation (Pydantic)
- ✅ Protected endpoints with dependency injection
- 🔜 Rate limiting
- 🔜 Input sanitization for custom text

---

## 🎯 Feature Roadmap

### Phase 1: MVP ✅
- [x] Authentication
- [x] Basic typing test
- [x] Rule-based adapter
- [x] Session storage
- [x] Simple analytics

### Phase 2: Enhancement
- [ ] Real-time WebSocket feedback
- [ ] Advanced progress charts
- [ ] Leaderboard & social features
- [ ] Custom text uploads

### Phase 3: Intelligence
- [ ] ML model training
- [ ] Personalized focus areas
- [ ] Predictive recommendations
- [ ] Error pattern analysis

### Phase 4: Scale
- [ ] Mobile app (React Native)
- [ ] Offline mode
- [ ] Enterprise features
- [ ] API for 3rd-party integrations

---

## 📝 Configuration Reference

### Backend (.env)
```env
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000

# Adapter selection
ADAPTER_TYPE=rule_based  # or "ml"

# Database
DATABASE_URL=sqlite:///./typing_trainer.db
# DATABASE_URL=postgresql://user:pass@localhost:5432/typing_trainer

# Features
ENABLE_REAL_TIME_FEEDBACK=True
ENABLE_ANALYTICS=True
ENABLE_LEADERBOARD=True

# Security
SECRET_KEY=change-this-in-production
```

### Frontend (vite.config.ts)
```typescript
VITE_API_URL=http://localhost:8000/api/v1
```

---

## 🚦 Next Steps

1. **Install dependencies** (see Getting Started)
2. **Start both servers** (backend on 8000, frontend on 5173)
3. **Create test user** (register at `/register`)
4. **Take a typing test** (`/typing-test`)
5. **View analytics** (`/dashboard`)
6. **Explore adapter** settings (`/settings`)
7. **Read detailed docs** (`docs/` folder)

---

This architecture whispers **"built with the future in mind"** at every level. 🚀
