/**
 * API Endpoints Quick Reference
 * Keystroke Recording and Analysis System
 */

/**
 * POST /api/v1/sessions/{session_id}/keystrokes
 * 
 * Submit a batch of keystroke events for analysis
 * 
 * Request Body:
 * {
 *   "events": [
 *     {
 *       "char": "a",
 *       "timestamp": 1234567890,
 *       "position": 0,
 *       "expected": "a",
 *       "is_correct": true,
 *       "elapsed_ms": 100
 *     }
 *   ],
 *   "context": "Difficulty 5",
 *   "test_duration_ms": 30000
 * }
 * 
 * Response: 201 Created
 * {
 *   "session_id": 1,
 *   "keystrokes_stored": 250,
 *   "error_classification": {
 *     "total_errors": 5,
 *     "by_type": {
 *       "substitution": 3,
 *       "insertion": 2,
 *       "deletion": 0,
 *       "transposition": 0
 *     },
 *     "levenshtein_distance": 5
 *   },
 *   "success": true
 * }
 */

/**
 * GET /api/v1/sessions/{session_id}/keystrokes
 * 
 * Retrieve all keystroke events for a session
 * 
 * Query Parameters:
 * - limit: int = 10000 (max keystrokes to return)
 * 
 * Response: 200 OK
 * [
 *   {
 *     "session_id": 1,
 *     "character": "a",
 *     "expected_character": "a",
 *     "position": 0,
 *     "timestamp_ms": 100,
 *     "is_correct": true,
 *     "error_type": null,
 *     "context": "Difficulty 5"
 *   }
 * ]
 */

/**
 * GET /api/v1/sessions/{session_id}/keystrokes/analysis
 * 
 * Get detailed error analysis for a session
 * 
 * Response: 200 OK
 * {
 *   "session_id": 1,
 *   "total_keystrokes": 250,
 *   "total_errors": 5,
 *   "error_classification": {
 *     "by_type": {
 *       "substitution": 3,
 *       "insertion": 2,
 *       "deletion": 0,
 *       "transposition": 0
 *     },
 *     "levenshtein_distance": 5
 *   },
 *   "errors_by_character": {
 *     "a": {
 *       "count": 2,
 *       "types": {
 *         "substitution": 1,
 *         "insertion": 1
 *       }
 *     },
 *     "s": {
 *       "count": 1,
 *       "types": {
 *         "substitution": 1
 *       }
 *     }
 *   },
 *   "detailed_errors": [
 *     {
 *       "position": 5,
 *       "expected": "a",
 *       "actual": "s",
 *       "error_type": "substitution",
 *       "timestamp_ms": 500
 *     }
 *   ]
 * }
 */

/**
 * GET /api/v1/sessions/{session_id}/weak-keys
 * 
 * Identify weak keys (high error rates) for a session
 * 
 * Response: 200 OK
 * {
 *   "session_id": 1,
 *   "total_characters": 26,
 *   "weak_keys": [
 *     {
 *       "character": "a",
 *       "attempts": 25,
 *       "errors": 5,
 *       "error_rate": 0.2,
 *       "error_types": {
 *         "substitution": 3,
 *         "insertion": 2
 *       },
 *       "positions": [5, 12, 18, 23, 45]
 *     },
 *     {
 *       "character": "s",
 *       "attempts": 20,
 *       "errors": 3,
 *       "error_rate": 0.15,
 *       "error_types": {
 *         "substitution": 2,
 *         "deletion": 1
 *       },
 *       "positions": [3, 17, 42]
 *     }
 *   ],
 *   "perfect_keys": ["t", "h", "e", "i", "o", "n", "r", "c", "l", "d", "u", "m", "f", "g", "p", "b", "w"]
 * }
 */

/**
 * Frontend Integration Example
 * 
 * // In TypingArea component after test completes
 * const submitKeystrokeBatch = async () => {
 *   const batch = {
 *     events: keystrokeHistory.map(event => ({
 *       char: event.character,
 *       timestamp: event.timestamp_ms,
 *       position: event.position,
 *       expected: event.expected_char,
 *       is_correct: event.character === event.expected_char,
 *       elapsed_ms: event.timestamp_ms
 *     })),
 *     context: `Difficulty ${difficulty}`,
 *     test_duration_ms: Date.now() - startTime
 *   };
 * 
 *   const response = await fetch(
 *     `/api/v1/sessions/${sessionId}/keystrokes`,
 *     {
 *       method: 'POST',
 *       headers: { 'Content-Type': 'application/json' },
 *       body: JSON.stringify(batch)
 *     }
 *   );
 * 
 *   const result = await response.json();
 *   console.log('Errors classified:', result.error_classification.by_type);
 * };
 */

/**
 * Results Component Integration Example
 * 
 * // In Results component
 * const [results, setResults] = useState(null);
 * 
 * useEffect(() => {
 *   // Fetch both analysis and weak-keys in parallel
 *   Promise.all([
 *     fetch(`/api/v1/sessions/${sessionId}/keystrokes/analysis`),
 *     fetch(`/api/v1/sessions/${sessionId}/weak-keys`)
 *   ])
 *   .then(([a, w]) => Promise.all([a.json(), w.json()]))
 *   .then(([analysis, weak]) => {
 *     setResults({
 *       errorAnalysis: analysis.error_classification,
 *       weakKeys: weak.weak_keys,
 *       perfectKeys: weak.perfect_keys
 *     });
 *   });
 * }, [sessionId]);
 * 
 * return (
 *   <ErrorVisualization
 *     errorClassification={results.errorAnalysis}
 *     weakKeys={results.weakKeys}
 *     perfectKeys={results.perfectKeys}
 *   />
 * );
 */

/**
 * Error Classification Types
 * 
 * INSERTION: User typed extra character
 * - Expected: "the"
 * - Typed: "thee"
 * - Classification: insertion at position 3
 * 
 * DELETION: User skipped a character
 * - Expected: "the"
 * - Typed: "te"
 * - Classification: deletion at position 1 (missing 'h')
 * 
 * SUBSTITUTION: User typed wrong character
 * - Expected: "the"
 * - Typed: "tha"
 * - Classification: substitution at position 2 ('e' → 'a')
 * 
 * TRANSPOSITION: User swapped adjacent characters
 * - Expected: "the"
 * - Typed: "teh"
 * - Classification: transposition at position 1 ('he' → 'eh')
 */
