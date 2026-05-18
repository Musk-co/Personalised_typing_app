# Adapter System Deep Dive

The adaptive engine that makes this trainer intelligent and extensible.

---

## 🧠 The Philosophy

The adapter system is the **core differentiator**—a completely decoupled module that can:
- ✅ Switch strategies at runtime (`rule_based` ↔ `ml`)
- ✅ Be extended without touching API code
- ✅ Support A/B testing different algorithms
- ✅ Grow from heuristics to ML seamlessly

---

## 🏗️ Architecture

### Base Adapter Interface

All adapters inherit from `BaseAdapter`:

```python
class BaseAdapter(ABC):
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
    
    @abstractmethod
    def get_initial_difficulty(user_profile: dict) -> int:
        """Determine starting difficulty"""
    
    @abstractmethod
    def analyze_session(session_data: dict) -> dict:
        """Analyze completed session"""
    
    @abstractmethod
    def recommend_next_difficulty(
        user_history: List[dict],
        current_performance: dict
    ) -> AdapterRecommendation:
        """Recommend difficulty for next session"""
    
    @abstractmethod
    def get_real_time_feedback(current_stats: dict) -> Optional[str]:
        """Provide mid-session guidance"""
```

### Three Methods, Endless Possibilities

| Method | Purpose | Input | Output |
|--------|---------|-------|--------|
| `get_initial_difficulty` | Bootstrap new users | User profile (exp level, goals) | Difficulty 1-10 |
| `analyze_session` | Introspect performance | Completed session metrics | Analysis report |
| `recommend_next_difficulty` | Intelligent progression | History + current perf | Recommendation + confidence |
| `get_real_time_feedback` | Live encouragement | Current WPM, accuracy | Motivational message |

---

## 📊 Rule-Based Adapter (MVP)

The default, production-ready adapter using threshold-based heuristics.

### Configuration

```python
RuleBasedAdapter(config={
    "accuracy_threshold": 85,      # % accuracy = "success"
    "wpm_threshold": 40,            # WPM = "success"
    "error_threshold": 5,           # Max errors before difficulty down
    "improvement_rate": 2           # Sessions until difficulty up
})
```

### Decision Logic

```
┌─────────────────────────────────┐
│   Analyze Last 2 Sessions       │
└──────────────┬──────────────────┘
               ↓
     ┌─────────────────────┐
     │ Both Excellent?     │
     └────┬──────────┬─────┘
        YES          NO
         ↓           ↓
      ┌──────┐   ┌──────────────────┐
      │ ↑ +1 │   │ Last Session Bad?│
      └──────┘   └────┬──────┬──────┘
                     YES      NO
                      ↓        ↓
                   ┌──────┐  ┌──────┐
                   │ ↓ -1 │  │ Keep │
                   └──────┘  └──────┘
```

### Example Recommendations

**Scenario 1: Beginner, 40 WPM, 92% accuracy**
```json
{
  "next_difficulty": 2,
  "focus_areas": ["Speed"],
  "reason": "Good accuracy! Try to increase speed.",
  "confidence": 0.80
}
```

**Scenario 2: Intermediate, 65 WPM, 78% accuracy**
```json
{
  "next_difficulty": 2,
  "focus_areas": ["Accuracy"],
  "reason": "Your speed is good, but accuracy needs work. Slow down.",
  "confidence": 0.75
}
```

**Scenario 3: Advanced, 85 WPM, 95% accuracy (2 sessions)**
```json
{
  "next_difficulty": 6,
  "focus_areas": ["Continue at this level"],
  "reason": "Excellent performance in last 2 sessions! Time to challenge yourself.",
  "confidence": 0.90
}
```

### Strengths
- ✅ Fast, deterministic
- ✅ Configurable, interpretable
- ✅ No training required
- ✅ Great for MVP/testing

### Limitations
- ❌ Can't learn patterns
- ❌ Treats all users the same
- ❌ No contextual awareness
- ❌ Can miss subtle performance signals

---

## 🤖 ML-Ready Adapter (Future)

A stub prepared for machine learning integration.

### Today's Implementation

Currently inherits from `RuleBasedAdapter` for immediate functionality:

```python
class MLAdapter(RuleBasedAdapter):
    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.model_version = "0.1.0-stub"
        self.ml_ready = False
    
    def load_model(self, model_path: str) -> bool:
        """Load ML model when ready"""
        # TODO: Load pre-trained model
        self.ml_ready = True
        return True
```

### Ready for Integration

When trained, swap implementations:

```python
def recommend_next_difficulty(self, user_history, current_perf):
    if self.ml_ready:
        features = self._extract_features(user_history)
        prediction = self.model.predict(features)
        confidence = self.model.predict_proba(features)
        return AdapterRecommendation(
            next_difficulty=prediction,
            focus_areas=self._get_ml_focus_areas(features),
            reason="ML model prediction",
            confidence=confidence
        )
    else:
        return super().recommend_next_difficulty(...)
```

### What ML Could Learn

```python
# Features from session history
features = {
    "avg_wpm": 58.3,
    "avg_accuracy": 91.2,
    "best_wpm": 72.5,
    "error_pattern_consistency": 0.78,
    "improvement_velocity": 0.15,  # WPM gained per session
    "sessions_completed": 25,
    "days_since_signup": 30,
    
    # Key-specific patterns
    "weakest_keys": ["q", "z", "x"],
    "shift_combination_success_rate": 0.82,
    "number_row_accuracy": 0.76,
    
    # Time-series features
    "recent_trend": "improving",
    "performance_volatility": 0.12,
    "fatigue_pattern": "slight decline in evening"
}

# Predict
next_difficulty = model.predict(features)  # 1-10
```

### Training Data Ready

The database captures everything needed:
- ✅ `error_details` - What went wrong
- ✅ `key_stats` - Per-key patterns
- ✅ `SessionMetrics` - Granular time-series
- ✅ `session_data` - Complete records

---

## 🔌 Pluggable Architecture

### How Adapters are Used

**1. Dependency Injection**
```python
# In FastAPI route
@router.post("/adapter/recommend")
async def get_recommendation(
    session_id: int,
    adapter: BaseAdapter = Depends(get_current_adapter)
):
    recommendation = adapter.recommend_next_difficulty(...)
    return recommendation
```

**2. Configuration-Based Selection**
```python
def get_current_adapter() -> BaseAdapter:
    adapter_type = settings.adapter_type  # From .env
    
    if adapter_type == "rule_based":
        return RuleBasedAdapter(config=user.adapter_config.parameters)
    elif adapter_type == "ml":
        adapter = MLAdapter(config=user.adapter_config.parameters)
        adapter.load_model("/models/typing_model.pkl")
        return adapter
    else:
        raise ValueError(f"Unknown adapter: {adapter_type}")
```

**3. Runtime Switching**
```python
# User can switch adapters in UI
POST /api/v1/adapter/config
{
  "adapter_type": "ml",
  "parameters": { ... }
}
```

### Custom Adapters

Create a custom adapter:

```python
# my_custom_adapter.py
from app.core.adapters.base import BaseAdapter

class AggresiveAdapter(BaseAdapter):
    """
    Pushes users harder.
    Increases difficulty more readily than rule-based.
    """
    
    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        self.aggressiveness = self.config.get("aggressiveness", 0.8)
    
    def recommend_next_difficulty(self, user_history, current_perf):
        # Custom logic: easier to level up
        if current_perf["performance_level"] in ["good", "excellent"]:
            next_diff = min(10, user_history[-1]["difficulty_level"] + 2)
        else:
            next_diff = user_history[-1]["difficulty_level"]
        
        return AdapterRecommendation(
            next_difficulty=next_diff,
            focus_areas=["Push yourself!"],
            reason="Aggressive progression mode",
            confidence=0.70
        )
```

Register and use:
```env
ADAPTER_TYPE=custom
# In code: CustomAdapterFactory.get("aggressive")
```

---

## 📊 Recommendation Details

### AdapterRecommendation Schema

```python
@dataclass
class AdapterRecommendation:
    next_difficulty: int          # 1-10, required
    focus_areas: List[str]        # What to work on
    reason: str                   # Explanation for user
    confidence: float             # 0.0-1.0
```

### How Confidence Works

```json
{
  "next_difficulty": 4,
  "confidence": 0.87
}
```

- **High confidence (0.8+)**: Strong signal, lots of data
- **Medium confidence (0.5-0.8)**: Mixed signals
- **Low confidence (<0.5)**: Not enough data, use with caution

**Frontend can use confidence to adjust UI**:
```typescript
if (recommendation.confidence < 0.6) {
  showWarning("Not enough data for this recommendation")
  suggestMoreSessions()
}
```

---

## 🔄 Real-Time Feedback

Adapters can provide mid-session coaching:

```python
def get_real_time_feedback(self, current_stats: dict) -> Optional[str]:
    wpm = current_stats["wpm"]
    accuracy = current_stats["accuracy"]
    
    if accuracy < 70:
        return "⚠️ Focus on accuracy - slow down if needed"
    elif wpm < 40 and accuracy >= 85:
        return "💨 You're accurate! Try to increase your speed"
    elif accuracy >= 90 and wpm >= 50:
        return "🔥 Excellent! You're in the zone"
    
    return None
```

**Sent to frontend every 5 seconds during test**:
```typescript
// Frontend
useEffect(() => {
  const interval = setInterval(async () => {
    const feedback = await adapter.get_real_time_feedback(metrics)
    if (feedback) displayMotivation(feedback)
  }, 5000)
  return () => clearInterval(interval)
}, [metrics])
```

---

## 🧪 A/B Testing Adapters

Store which adapter was used:

```python
# In session data
session.adapter_used = "rule_based"  # or "ml"
session.adapter_recommendation = recommendation
```

Query results by adapter:

```sql
SELECT adapter_used, AVG(accuracy) as avg_acc, COUNT(*) as sessions
FROM typing_sessions
WHERE user_id = ?
GROUP BY adapter_used
```

Analyze which works best per user:
- Adapter A: 89% accuracy, 55 WPM
- Adapter B: 91% accuracy, 52 WPM

→ Maybe this user benefits more from Adapter B

---

## 📈 Versioning Adapters

Support multiple versions:

```python
class MLAdapter:
    model_version = "1.0.0"  # Track version
    
    # Load specific version
    def load_model(self, version: str = "latest"):
        path = f"/models/typing_{version}.pkl"
        self.model = joblib.load(path)
```

Database tracks which version:

```python
user_config.adapter_type = "ml"
user_config.parameters = {"model_version": "1.0.0"}
```

---

## 🚀 Future Extensions

### Idea 1: Ensemble Adapters
```python
class EnsembleAdapter(BaseAdapter):
    def __init__(self):
        self.adapters = [RuleBasedAdapter(), MLAdapter()]
    
    def recommend_next_difficulty(self, history, perf):
        # Vote from multiple adapters
        recommendations = [a.recommend(...) for a in self.adapters]
        # Average or weighted vote
        return aggregate(recommendations)
```

### Idea 2: User-Specific Adapters
```python
class PersonalizedAdapter(BaseAdapter):
    def __init__(self, user_profile):
        self.style = user_profile.learning_style  # Aggressive, conservative, steady
        self.config = self._get_config_for_style(self.style)
```

### Idea 3: Time-Aware Adapters
```python
class TimeAwareAdapter(BaseAdapter):
    def get_real_time_feedback(self, stats):
        time_of_day = datetime.now().hour
        if time_of_day > 22:  # Late night
            return "💤 Getting tired? Consider stopping for today."
```

---

## 📚 Implementation Checklist

- [x] Abstract `BaseAdapter` interface
- [x] `RuleBasedAdapter` implementation
- [x] `MLAdapter` stub
- [ ] ML model training pipeline
- [ ] Model versioning system
- [ ] Adapter factory/registry
- [ ] A/B testing framework
- [ ] Adapter performance analytics
- [ ] User-specific adapter selection
- [ ] Ensemble adapters

---

This system is designed to be **infinitely extensible** while remaining simple today. 🚀
