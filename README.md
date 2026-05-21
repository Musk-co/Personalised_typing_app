# Personalized Adaptive Typing Trainer

A complete, production-grade blueprint for an intelligent typing training application.

## 🎯 What This Is

This is a **full-stack monorepo** with:
- ✅ **React + TypeScript + Tailwind** frontend
- ✅ **FastAPI** backend with pluggable adapters
- ✅ **SQLite/PostgreSQL** database with extensible schema
- ✅ **Real-time metrics** and progress tracking
- ✅ **ML-ready architecture** (rule-based MVP, ML stub ready)
- ✅ **Comprehensive documentation**

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.10+
Node.js 18+
```

### Backend

```bash
cd backend

# Create environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env

# Run
python -m app.main
```

Server: `http://localhost:8000`
Docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

App: `http://localhost:5173`

## 📁 Project Structure

```
Personalized Typing App/
├── backend/                 # FastAPI server
│   ├── app/
│   │   ├── api/            # REST endpoints
│   │   ├── core/           # Adapters & engine
│   │   ├── db/             # Database models
│   │   └── utils/
│   ├── requirements.txt
│   └── README.md
│
├── frontend/               # React app
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/          # State (Zustand)
│   │   ├── services/       # API client
│   │   └── types/
│   ├── package.json
│   └── README.md
│
├── shared/                 # Shared types
├── docs/                   # Architecture docs
└── README.md              # This file
```

## 📚 Documentation

Start here:

1. **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design, principles, data flow
2. **[DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)** - Data models in depth
3. **[API_SPEC.md](docs/API_SPEC.md)** - Complete REST API reference
4. **[ADAPTER_SYSTEM.md](docs/ADAPTER_SYSTEM.md)** - How the intelligence works

## 🧠 Key Features

### Dynamic Adaptive Difficulty
- **Rule-based adapter** (MVP): Configurable thresholds
- **ML-ready stub**: Prepared for TensorFlow/sklearn
- **Pluggable**: Swap adapters at runtime

### Comprehensive Metrics
- Real-time WPM and accuracy
- Error pattern analysis
- Per-key statistics
- Progress trends

### Extensible Schema
- JSON fields for future features
- Prepared for ML integration
- SQLite → PostgreSQL migration path
- User-specific customization

### Real-Time Feedback
- Mid-session coaching
- Live metrics updates
- Motivational messages
- Performance alerts

## 🔌 Adapter System

The heart of the system. Create your own:

```python
class MyAdapter(BaseAdapter):
    def recommend_next_difficulty(self, history, perf):
        # Your logic
        return AdapterRecommendation(
            next_difficulty=4,
            focus_areas=["Speed"],
            reason="...",
            confidence=0.85
        )
```

See [ADAPTER_SYSTEM.md](docs/ADAPTER_SYSTEM.md) for details.

## 🛠️ Tech Stack

**Backend**
- FastAPI 0.104
- SQLAlchemy 2.0
- Pydantic 2.5
- Python 3.10+

**Frontend**
- React 18.2
- TypeScript 5.3
- Tailwind CSS 3.4
- Zustand (state)
- Axios (HTTP)

**Database**
- SQLite (dev)
- PostgreSQL (production-ready)

## 📈 Project Roadmap

### Phase 1: MVP ✅
- [x] User auth & profiles
- [x] Typing test engine
- [x] Rule-based adapter
- [x] Basic analytics
- [x] Database schema

### Phase 2: Enhancement
- [ ] Real-time WebSocket updates
- [ ] Advanced charts (Chart.js)
- [ ] Custom text uploads
- [ ] Keyboard layouts

### Phase 3: Intelligence
- [ ] ML model training
- [ ] Pattern detection
- [ ] Predictive recommendations
- [ ] Personalized coaching

### Phase 4: Scale
- [ ] Mobile app
- [ ] Offline mode
- [ ] Enterprise features
- [ ] Public API

## 🎨 Design Philosophy

**"Don't Hard-Code Limits"**

- No magic numbers (all configurable)
- Adapters are pluggable (not hardcoded)
- Database prepared for growth (SQLite → PostgreSQL)
- Types extensible (JSON fields)
- APIs versioned (`/api/v1`)

## 🔐 Security

- ✅ JWT authentication
- ✅ Password hashing (bcrypt)
- ✅ CORS configured
- ✅ Input validation (Pydantic)
- ✅ Protected endpoints
- 🔜 Rate limiting
- 🔜 HTTPS enforcement

## 📊 API Overview

```
/api/v1/auth          # Login, register, token
/api/v1/sessions      # Typing tests CRUD
/api/v1/users         # Profiles & settings
/api/v1/analytics     # Stats & leaderboard
/api/v1/adapter       # Recommendations & config
```

See [API_SPEC.md](docs/API_SPEC.md) for complete reference.

## 🧪 Testing

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## 🚢 Deployment

**Docker** (coming):
```bash
docker-compose up
```

**Manual**:
```bash
# Backend: uvicorn app.main:app --host 0.0.0.0 --port 8000
# Frontend: npm run build && serve dist
```

## 📝 Configuration

### Backend (.env)
```env
DEBUG=True
ADAPTER_TYPE=rule_based
DATABASE_URL=sqlite:///./typing_trainer.db
SECRET_KEY=your-secret-key
```

### Frontend (vite.config.ts)
```typescript
VITE_API_URL=http://localhost:8000/api/v1
```

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Write tests
4. Submit PR

## 📞 Support

See individual READMEs:
- [backend/README.md](backend/README.md)
- [frontend/README.md](frontend/README.md)

## 📜 License

MIT

---

**Built with the future in mind** 🚀

This architecture is designed to evolve from a simple MVP to an ML-powered platform without major refactoring. Every choice—from the pluggable adapters to the JSON-friendly schema—was made with extensibility in mind.

Start simple. Scale smart.
