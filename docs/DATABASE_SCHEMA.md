# Database Schema Documentation

Comprehensive guide to the Personalized Adaptive Typing Trainer database.

---

## 📊 Entity-Relationship Diagram

```
┌─────────────┐
│   Users     │
├─────────────┤
│ id (PK)     │─────────┐
│ email       │         │
│ username    │         │
│ password    │         │
│ created_at  │         │
└─────────────┘         │
      │                 │
      ├─────────────────┼──────────────────────────────┐
      │                 │                              │
      │                 ↓                              │
      │    ┌────────────────────────┐                 │
      │    │ TypingSessions         │                 │
      │    ├────────────────────────┤                 │
      │    │ id (PK)                │                 │
      │    │ user_id (FK) ←─────────┴─────────────────┤
      │    │ difficulty_level       │                 │
      │    │ wpm, accuracy, errors  │                 │
      │    │ error_details (JSON)   │                 │
      │    │ key_stats (JSON)       │                 │
      │    │ adapter_used           │                 │
      │    │ adapter_recommendation │                 │
      │    │ started_at, ended_at   │                 │
      │    │ created_at             │                 │
      │    └────────────────────────┘                 │
      │             │                                  │
      │             ├──────────────┐                  │
      │             │              │                  │
      │             ↓              ↓                  │
      │    ┌──────────────┐  ┌────────────────┐     │
      │    │SessionMetrics│  │UserStatSnapshot│     │
      │    ├──────────────┤  ├────────────────┤     │
      │    │ id           │  │ id             │     │
      │    │ session_id   │  │ user_id (FK)───┴─────┤
      │    │ timestamp    │  │ total_sessions │     │
      │    │ current_wpm  │  │ avg_wpm        │     │
      │    │ curr_acc.    │  │ best_wpm       │     │
      │    │adapter_state │  │ improvement%   │     │
      │    │              │  │ rank, percentile
      │    └──────────────┘  └────────────────┘
      │
      ├─────────────────────────────────────┐
      │                                     │
      ↓                                     ↓
┌──────────────────────┐          ┌──────────────────┐
│UserAdapterConfig     │          │UserPreference    │
├──────────────────────┤          ├──────────────────┤
│ id                   │          │ id               │
│ user_id (FK) ────────┤          │ user_id (FK) ────┤
│ adapter_type         │          │ theme            │
│ parameters (JSON)    │          │ notifications    │
│ custom_rules (JSON)  │          │ language         │
│ created_at, upd.     │          │ keyboard_layout  │
└──────────────────────┘          │ sound_enabled    │
                                  │ difficulty_adj.  │
                                  │ extra_settings   │
                                  └──────────────────┘
```

---

## 📋 Table Definitions

### `users`
Core user account table.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | User email (login) |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Display name |
| `full_name` | VARCHAR(255) | NULLABLE | User's full name |
| `hashed_password` | VARCHAR(255) | NOT NULL | bcrypt password hash |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account status |
| `created_at` | DATETIME | DEFAULT NOW() | Account creation time |
| `updated_at` | DATETIME | DEFAULT NOW() | Last update time |

**Indexes**: `email`, `username`, `created_at`

**Relationships**:
- `1:N` → `TypingSessions` (cascade delete)
- `1:1` → `UserPreference` (cascade delete)
- `1:1` → `UserAdapterConfig` (cascade delete)

---

### `typing_sessions`
The core table capturing every typing test. This is where the magic happens.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY | Session identifier |
| `user_id` | INTEGER | FOREIGN KEY, NOT NULL, INDEX | Owner of session |
| `test_type` | VARCHAR(50) | DEFAULT 'standard' | Type: standard, coding, custom |
| `difficulty_level` | INTEGER | DEFAULT 1 | 1-10 scale |
| `status` | VARCHAR(20) | DEFAULT 'in_progress' | in_progress, completed, paused |
| `text_prompt` | TEXT | NOT NULL | The text to type |
| `text_typed` | TEXT | NOT NULL | What user actually typed |
| `custom_text` | BOOLEAN | DEFAULT FALSE | Was this user-provided text? |
| `started_at` | DATETIME | DEFAULT NOW() | Test start time |
| `ended_at` | DATETIME | NULLABLE | Test end time |
| `duration_seconds` | INTEGER | NULLABLE | Total duration |
| `wpm` | FLOAT | NULLABLE | Words per minute (final) |
| `accuracy` | FLOAT | NULLABLE | Accuracy % (final) |
| `errors` | INTEGER | DEFAULT 0 | Total errors count |
| `key_presses` | INTEGER | DEFAULT 0 | Total keystrokes |
| `error_details` | JSON | DEFAULT '{}' | Detailed error map: `{position: {expected, actual}}` |
| `key_stats` | JSON | DEFAULT '{}' | Per-key analysis: `{key: {attempts, errors, positions}}` |
| `adapter_used` | VARCHAR(50) | NULLABLE | Which adapter was active |
| `adapter_recommendation` | JSON | NULLABLE | Recommendation received |
| `created_at` | DATETIME | DEFAULT NOW(), INDEX | Record creation |
| `updated_at` | DATETIME | DEFAULT NOW() | Last update |

**Indexes**: `user_id`, `created_at`, `status`, `difficulty_level`

**JSON Schemas**:

`error_details`:
```json
{
  "0": { "expected": "a", "actual": "s" },
  "5": { "expected": "b", "actual": "" },
  "10": { "expected": "c", "actual": "c" }
}
```

`key_stats`:
```json
{
  "a": { "attempts": 15, "errors": 2, "error_positions": [0, 15] },
  "b": { "attempts": 10, "errors": 1, "error_positions": [5] },
  "space": { "attempts": 8, "errors": 0, "error_positions": [] }
}
```

`adapter_recommendation`:
```json
{
  "next_difficulty": 3,
  "focus_areas": ["Accuracy"],
  "reason": "Good speed, focus on accuracy",
  "confidence": 0.85
}
```

---

### `session_metrics`
Granular real-time metrics captured during a session.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY | Metric snapshot ID |
| `session_id` | INTEGER | FOREIGN KEY, NOT NULL, INDEX | Parent session |
| `timestamp` | DATETIME | DEFAULT NOW() | When this metric was recorded |
| `current_wpm` | FLOAT | NOT NULL | WPM at this point |
| `current_accuracy` | FLOAT | NOT NULL | Accuracy % at this point |
| `errors_so_far` | INTEGER | NOT NULL | Cumulative errors |
| `characters_typed` | INTEGER | NOT NULL | Total characters |
| `adapter_state` | JSON | NULLABLE | Adapter internal state (for analysis) |
| `created_at` | DATETIME | DEFAULT NOW() | Record creation |

**Indexes**: `session_id`, `timestamp`

**Use Case**: 
- Track progress over time within a session
- Detect when performance degrades
- Visualize typing curves
- Train ML models on time-series data

---

### `user_preferences`
User settings and preferences (one-to-one with users).

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY | Preference set ID |
| `user_id` | INTEGER | FOREIGN KEY UNIQUE, NOT NULL | Parent user |
| `theme` | VARCHAR(20) | DEFAULT 'light' | light, dark, auto |
| `notifications_enabled` | BOOLEAN | DEFAULT TRUE | Email/push notifications |
| `language` | VARCHAR(10) | DEFAULT 'en' | i18n language code |
| `keyboard_layout` | VARCHAR(20) | DEFAULT 'qwerty' | qwerty, dvorak, colemak, etc. |
| `sound_enabled` | BOOLEAN | DEFAULT TRUE | Audio feedback |
| `difficulty_auto_adjust` | BOOLEAN | DEFAULT TRUE | Auto difficulty change |
| `extra_settings` | JSON | DEFAULT '{}' | Extensible custom settings |
| `created_at` | DATETIME | DEFAULT NOW() | Creation time |
| `updated_at` | DATETIME | DEFAULT NOW() | Update time |

**Purpose**: Per-user customization without modifying core schema

---

### `user_adapter_configs`
Adapter configuration and customization per user.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY | Config ID |
| `user_id` | INTEGER | FOREIGN KEY UNIQUE, NOT NULL | Parent user |
| `adapter_type` | VARCHAR(50) | DEFAULT 'rule_based' | Adapter to use |
| `parameters` | JSON | DEFAULT '{}' | Adapter-specific config |
| `custom_rules` | JSON | DEFAULT '{}' | Custom rules (rule-based adapter) |
| `created_at` | DATETIME | DEFAULT NOW() | Creation time |
| `updated_at` | DATETIME | DEFAULT NOW() | Update time |

**Examples**:

`parameters` (rule-based):
```json
{
  "accuracy_threshold": 85,
  "wpm_threshold": 40,
  "error_threshold": 5,
  "improvement_rate": 2
}
```

`custom_rules`:
```json
{
  "if_wpm_above": 70,
  "then_increase_difficulty_by": 2,
  "min_sessions_required": 1
}
```

---

### `user_stat_snapshots`
Pre-computed statistics for fast queries (denormalized).

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY | Snapshot ID |
| `user_id` | INTEGER | FOREIGN KEY, NOT NULL, INDEX | User |
| `total_sessions` | INTEGER | DEFAULT 0 | Total test count |
| `avg_wpm` | FLOAT | NULLABLE | Average WPM |
| `best_wpm` | FLOAT | NULLABLE | Personal best |
| `avg_accuracy` | FLOAT | NULLABLE | Average accuracy |
| `total_errors` | INTEGER | DEFAULT 0 | Cumulative errors |
| `total_practice_hours` | FLOAT | DEFAULT 0 | Total time |
| `weekly_improvement` | FLOAT | NULLABLE | % improvement week-over-week |
| `monthly_improvement` | FLOAT | NULLABLE | % improvement month-over-month |
| `rank` | INTEGER | NULLABLE | Global rank by WPM |
| `percentile` | FLOAT | NULLABLE | Percentile ranking |
| `period_start` | DATETIME | NOT NULL | Snapshot period start |
| `period_end` | DATETIME | NOT NULL | Snapshot period end |
| `created_at` | DATETIME | DEFAULT NOW() | Creation time |

**Purpose**: 
- Cache complex aggregations
- Fast leaderboard queries
- Performance trends without computing every query
- Refresh nightly or on-demand

**Example**: 
```sql
-- Fast leaderboard query (no joins needed)
SELECT rank, username, best_wpm, avg_accuracy, total_sessions
FROM user_stat_snapshots
WHERE period_end = (SELECT MAX(period_end) FROM user_stat_snapshots)
ORDER BY rank ASC
LIMIT 10
```

---

## 🔑 Key Design Decisions

### 1. **JSON Fields for Extensibility**
- `error_details`, `key_stats`, `adapter_recommendation`, `extra_settings`, etc.
- Can evolve without schema migrations
- Perfect for machine learning features

### 2. **Granular Metrics (`session_metrics`)**
- Instead of just final metrics, capture snapshots
- Enables real-time feedback and time-series analysis
- Foundation for ML training data

### 3. **Denormalized Stats Table**
- Pre-computed `user_stat_snapshots` for fast analytics
- Refresh periodically (nightly or on-demand)
- Prevents expensive aggregations on production queries

### 4. **Status Field Pattern**
- `status` in `typing_sessions` allows pausing/resuming
- Easy to track incomplete or abandoned tests
- Supports future "continue session" feature

### 5. **Adapter Integration**
- `adapter_used` and `adapter_recommendation` stored together
- Enables A/B testing different adapters
- Can analyze which adapter works best per user

---

## 📈 Query Examples

### Get user's typing progress over last 30 days
```sql
SELECT DATE(started_at) as date, AVG(wpm) as avg_wpm, AVG(accuracy) as avg_accuracy
FROM typing_sessions
WHERE user_id = ? AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(started_at)
ORDER BY date ASC
```

### Find weak keys for a user
```sql
SELECT 
  JSON_EXTRACT(key_stats, '$.*.errors') as errors,
  JSON_EXTRACT(key_stats, '$.*.attempts') as attempts
FROM typing_sessions
WHERE user_id = ?
ORDER BY created_at DESC
LIMIT 10
```

### Get leaderboard
```sql
SELECT rank, user_id, best_wpm, avg_accuracy, total_sessions
FROM user_stat_snapshots
WHERE period_end = (SELECT MAX(period_end) FROM user_stat_snapshots)
ORDER BY rank ASC
LIMIT 10
```

---

## 🔄 Migrations Strategy

Uses **Alembic** for version control:

```
backend/app/db/migrations/
├── env.py
├── script.py.mako
└── versions/
    ├── 001_initial_schema.py
    ├── 002_add_adapter_config.py
    └── ...
```

Create migration:
```bash
alembic revision --autogenerate -m "Add adapter_config table"
```

Apply migrations:
```bash
alembic upgrade head
```

---

## 📊 Indexes Strategy

**High-Traffic Queries**:
- `typing_sessions(user_id)` - User's sessions
- `typing_sessions(created_at)` - Recent sessions
- `user_stat_snapshots(period_end)` - Latest stats

**Composite Indexes**:
- `typing_sessions(user_id, created_at)` - User's recent sessions
- `session_metrics(session_id, timestamp)` - Session metrics in order

---

## 🛡️ Data Integrity

**Constraints**:
- `NOT NULL` on critical fields
- `UNIQUE` on email, username
- `FOREIGN KEY` with CASCADE DELETE for orphan cleanup
- `CHECK` constraints for bounds (difficulty 1-10, accuracy 0-100)

**Triggers** (future):
- Auto-update `user_stat_snapshots` on session completion
- Cascade `updated_at` timestamps

---

This schema is **built to scale** from SQLite development to PostgreSQL production without code changes. 🚀
