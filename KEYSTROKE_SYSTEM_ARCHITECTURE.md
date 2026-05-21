# Typing Engine Keystroke System Architecture

## System Overview

The keystroke system is the "nerve system" of the typing app - it captures every keystroke with millisecond precision, classifies errors, and provides detailed analytics that make users feel "nothing goes unnoticed."

## Core Components

### 1. Frontend Keystroke Capture (TypingArea.tsx)

**Responsibility**: Capture keystrokes at the point of user input

```
┌─────────────────────────────────────────┐
│         User Types Character            │
│                  ↓                       │
│    onKeyDown event fires                │
│                  ↓                       │
│  Record timestamp (millisecond)         │
│  Record character                       │
│  Record position in text                │
│  Record expected character              │
│                  ↓                       │
│  Add to keystrokeHistory array          │
│                  ↓                       │
│  Update visual feedback (green/red)     │
│  Calculate real-time WPM/accuracy       │
└─────────────────────────────────────────┘
```

**Key Data Structure**:
```typescript
interface KeystrokeEvent {
  character: string           // What user typed
  position: number            // Position in test text
  timestamp_ms: number        // Millisecond timestamp
  expected_char: string       // What should be typed
}
```

**Features**:
- Keystroke pooling (prevent event flooding)
- Blur detection (auto-pause test)
- Real-time character feedback
- Live metrics calculation

### 2. Frontend State Management (useTyping.ts)

**Responsibility**: Maintain keystroke history and state

- `keystrokeHistory`: Array of all keystroke events
- `errorLog`: Detailed errors with classification
- `realTimeMetrics`: Live WPM/accuracy updates
- `recordKeystroke()`: Add keystroke to history
- `calculateRealtimeMetrics()`: Update metrics

### 3. Frontend Test Completion (TypingArea.tsx)

**Responsibility**: Submit keystroke batch for backend processing

```
Test Completes
      ↓
submitKeystrokeBatch() called
      ↓
Format keystroke array:
{
  events: [
    { char, timestamp, position, expected, is_correct }
  ],
  context: "Difficulty X",
  test_duration_ms: Y
}
      ↓
POST /sessions/{id}/keystrokes
      ↓
Receive error classification response
      ↓
Fetch /keystrokes/analysis
Fetch /weak-keys
      ↓
Display Results component
```

### 4. Backend Keystroke Processing (keystrokes.py)

**Responsibility**: Process keystroke batch and classify errors

#### Endpoint: POST /api/v1/sessions/{session_id}/keystrokes

**Process**:
```python
1. Validate session exists
2. Get expected text from session
3. Build typed text from keystroke events
4. Initialize ErrorClassifier
5. Call classify_errors(expected, typed)
   ↓
   For each keystroke:
   - Determine if correct
   - Find corresponding error (if any)
   - Classify error type:
     * SUBSTITUTION: wrong character
     * INSERTION: extra character
     * DELETION: missing character
     * TRANSPOSITION: swapped characters
   ↓
6. Store each keystroke with error classification
7. Calculate Levenshtein distance
8. Group errors by type
9. Return classification summary
```

### 5. Error Classification (error_detector.py)

**Responsibility**: Intelligent error detection using Levenshtein algorithm

**Key Algorithm**:
```python
def levenshtein_distance(s1, s2):
    """
    Calculate minimum edit distance between strings
    
    Edits:
    - Insertion: add character
    - Deletion: remove character
    - Substitution: change character
    - Transposition: swap adjacent characters
    """
```

**Error Classification**:
```python
def classify_errors(expected, typed):
    """
    For each character position:
    1. Compare expected vs typed
    2. If mismatch, determine error type
    3. Return DetailedError with:
       - position: where error occurred
       - expected: expected character
       - actual: typed character
       - error_type: INSERTION/DELETION/SUBSTITUTION/TRANSPOSITION
       - timestamp_ms: when error occurred
    """
```

### 6. Backend Analysis Endpoints

#### GET /api/v1/sessions/{session_id}/keystrokes/analysis

Returns detailed error analysis:
- Total errors grouped by type
- Per-character error breakdown
- Error timeline (first 50 errors)
- Levenshtein distance

```json
{
  "total_errors": 5,
  "by_type": {
    "substitution": 3,
    "insertion": 2,
    "deletion": 0,
    "transposition": 0
  },
  "levenshtein_distance": 5,
  "errors_by_character": {
    "a": { "count": 2, "types": { "substitution": 1, "insertion": 1 } },
    "s": { "count": 1, "types": { "substitution": 1 } }
  }
}
```

#### GET /api/v1/sessions/{session_id}/weak-keys

Returns per-character performance analysis:
- Characters with highest error rates
- Number of attempts per character
- Error type distribution per character
- Perfect keys (0 errors, ≥5 attempts)

```json
{
  "weak_keys": [
    {
      "character": "a",
      "attempts": 25,
      "errors": 5,
      "error_rate": 0.2,
      "error_types": { "substitution": 3, "insertion": 2 },
      "positions": [5, 12, 18, 23, 45]
    }
  ],
  "perfect_keys": ["t", "h", "e", "i", "o", "n", "r"]
}
```

### 7. Results Display (Results.tsx)

**Responsibility**: Visualize typing performance

**Features**:
- Accuracy percentage
- Levenshtein distance
- Total keystrokes captured
- Most common error type
- Detailed error visualization
- Perfect keys display
- Actionable insights

### 8. Error Visualization (ErrorVisualization.tsx)

**Responsibility**: Visual representation of errors

**Displays**:
1. **Error Type Breakdown**: Bar chart showing distribution of error types
2. **Weak Key Heatmap**: Color intensity based on error rate
3. **Error Timeline**: Chronological list of each error with context
4. **Perfect Keys**: Badge display of flawlessly typed characters

## Data Flow Diagram

```
┌─────────────────────────────────┐
│    USER TYPING INTERFACE        │
│  (TypingArea.tsx)               │
│                                 │
│  onKeyDown → Record keystroke   │
│  Visual feedback (green/red)    │
│  Real-time metrics              │
└──────────────┬──────────────────┘
               │
               ↓ keystrokeHistory array
┌──────────────────────────────────┐
│   Frontend State (useTyping.ts)   │
│                                  │
│  keystrokeHistory: []            │
│  errorLog: []                    │
│  realTimeWpm: number             │
│  realTimeAccuracy: number        │
└──────────────┬───────────────────┘
               │
        Test Completes
               │
               ↓ POST keystroke batch
┌─────────────────────────────────────────┐
│     Backend Processing                  │
│  (keystrokes.py)                        │
│                                         │
│  1. Validate session                    │
│  2. Build expected text                 │
│  3. Build typed text                    │
│  4. ErrorClassifier.classify_errors()   │
│  5. Store Keystroke records (DB)        │
│  6. Return classification summary       │
└──────────────┬──────────────────────────┘
               │
               ↓ error_classification response
┌──────────────────────────────────┐
│    Results Component             │
│  (Results.tsx)                   │
│                                  │
│  GET /keystrokes/analysis        │
│  GET /weak-keys                  │
│                                  │
│  Display metrics                 │
│  Display ErrorVisualization      │
└─────────────────────────────────┘
```

## Database Schema

### Keystroke Table
```sql
CREATE TABLE keystrokes (
  id INTEGER PRIMARY KEY,
  session_id INTEGER FOREIGN KEY,
  character VARCHAR(1),                    -- What user typed
  expected_character VARCHAR(1),           -- What should be typed
  position INTEGER,                        -- Position in text
  timestamp_ms FLOAT,                      -- Millisecond timestamp
  is_correct BOOLEAN,                      -- Correctness flag
  error_type VARCHAR(50),                  -- Error classification
  context VARCHAR(255),                    -- Additional context
  created_at DATETIME
);
```

**Indexes**: 
- `session_id` (for fast retrieval by session)
- `created_at` (for chronological queries)

## Error Classification Logic

### SUBSTITUTION
```
Expected: "the"
Typed:    "tha"
Position: 2
Error:    'e' was replaced with 'a'
```

### INSERTION  
```
Expected: "the"
Typed:    "thee"
Position: 3
Error:    Extra 'e' inserted
```

### DELETION
```
Expected: "the"
Typed:    "te"
Position: 1
Error:    Missing 'h'
```

### TRANSPOSITION
```
Expected: "the"
Typed:    "teh"
Position: 1-2
Error:    'h' and 'e' swapped
```

## Performance Characteristics

### Capture
- Keystroke capture: O(1) per keystroke
- History append: O(1) amortized
- Real-time metrics: O(n) per keystroke

### Processing
- Levenshtein distance: O(n × m) where n, m = text length
- Error classification: O(n × m)
- Per-character analysis: O(n)

### Storage
- Keystroke record: ~150 bytes per keystroke
- For 60-minute typing test @ 80 WPM: ~50,000 keystrokes ≈ 7.5MB

## Security & Validation

1. **Session Validation**: Every keystroke submission validated against session ID
2. **Data Integrity**: Keystroke order preserved via position column
3. **Input Validation**: Character input validated to be single character
4. **Error Handling**: Graceful degradation on processing errors

## Future Enhancements

1. **WebSocket Real-time**: Push live metrics during test
2. **ML Integration**: Feed error patterns to ML adapter
3. **Performance Analytics**: Track improvement trends
4. **Weak Key Training**: Targeted practice mode
5. **Keyboard Heatmap**: Visual keyboard with error heat
6. **Error Recovery**: Track how quickly users fix mistakes

## Testing Checklist

- [ ] Keystroke capture with various key types (letters, numbers, symbols)
- [ ] Error classification accuracy (all 4 error types)
- [ ] Levenshtein distance calculation correctness
- [ ] Backend endpoint validation
- [ ] Database storage and retrieval
- [ ] Results component data fetching
- [ ] Error visualization rendering
- [ ] Performance under high keystroke volume
- [ ] Mobile responsiveness

