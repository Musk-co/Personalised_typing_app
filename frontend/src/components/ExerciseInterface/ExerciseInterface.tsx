/**
 * Adaptive Exercise Interface Component
 *
 * Displays personalized exercises generated from user's weak keys and error patterns.
 * Never static - every exercise is fresh, born from your specific mistakes.
 *
 * Features:
 * - Generated exercise prompt
 * - Real-time keystroke capture
 * - Performance metrics during exercise
 * - Immediate feedback
 * - Difficulty adjustment recommendation
 */

import React, { useEffect, useState, useRef } from 'react';
import styles from './ExerciseInterface.module.css';

interface Exercise {
  exercise_id: number;
  text_prompt: string;
  exercise_type: string;
  difficulty: number;
  focus_chars: string[];
  description: string;
  expected_duration_seconds: number;
  generated_at: string;
}

interface PerformanceMetrics {
  accuracy: number;
  wpm: number;
  errors: number;
  currentCharIndex: number;
  timeElapsed: number;
}

interface ExerciseInterfaceProps {
  userId: number;
  onExerciseComplete?: (metrics: any) => void;
}

export const ExerciseInterface: React.FC<ExerciseInterfaceProps> = ({
  userId,
  onExerciseComplete,
}) => {
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isActive, setIsActive] = useState(false);
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    accuracy: 0,
    wpm: 0,
    errors: 0,
    currentCharIndex: 0,
    timeElapsed: 0,
  });

  const inputRef = useRef<HTMLInputElement>(null);
  const startTimeRef = useRef<number | null>(null);
  const keystrokesRef = useRef<string>('');

  // Load exercise on mount
  useEffect(() => {
    const loadExercise = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/v1/users/${userId}/exercises/current`);

        if (response.ok) {
          const data = await response.json();
          if (data) {
            setExercise(data);
          } else {
            // No current exercise - generate new one
            const generateResponse = await fetch(
              `/api/v1/users/${userId}/exercises/generate`,
              { method: 'POST' }
            );

            if (generateResponse.ok) {
              const generatedData = await generateResponse.json();
              setExercise(generatedData);
            }
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load exercise');
      } finally {
        setLoading(false);
      }
    };

    loadExercise();
  }, [userId]);

  // Start exercise
  const handleStartExercise = () => {
    setIsActive(true);
    startTimeRef.current = Date.now();
    keystrokesRef.current = '';
    inputRef.current?.focus();
  };

  // Handle keystroke input
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isActive || !exercise) return;

    const char = e.key === 'Enter' ? '\n' : e.key;
    keystrokesRef.current += char;

    // Calculate metrics in real-time
    const timeElapsed = Math.floor((Date.now() - (startTimeRef.current || Date.now())) / 1000);
    const promptText = exercise.text_prompt;
    const typedText = keystrokesRef.current;

    // Calculate accuracy
    let correctChars = 0;
    for (let i = 0; i < Math.min(typedText.length, promptText.length); i++) {
      if (typedText[i] === promptText[i]) {
        correctChars++;
      }
    }

    const accuracy =
      typedText.length > 0 ? (correctChars / promptText.length) * 100 : 0;

    // Calculate WPM
    const words = typedText.trim().split(/\s+/).length;
    const minutes = Math.max(timeElapsed / 60, 0.1);
    const wpm = words / minutes;

    // Count errors
    const errors = Math.max(0, typedText.length - correctChars);

    setMetrics({
      accuracy: Math.min(accuracy, 100),
      wpm: Math.round(wpm),
      errors,
      currentCharIndex: typedText.length,
      timeElapsed,
    });

    // Check if exercise complete
    if (typedText.length >= promptText.length) {
      completeExercise(accuracy, wpm, errors, timeElapsed);
    }
  };

  const completeExercise = async (
    accuracy: number,
    wpm: number,
    errors: number,
    duration: number
  ) => {
    setIsActive(false);

    if (!exercise) return;

    try {
      const response = await fetch(
        `/api/v1/users/${userId}/exercises/${exercise.exercise_id}/submit`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            accuracy: Math.round(accuracy),
            wpm: Math.round(wpm),
            errors,
            duration_seconds: duration,
            difficulty_felt: accuracy < 85 ? 'too_hard' : accuracy > 95 ? 'easy' : 'fair',
            confidence_level: 5, // Default, could be user-rated
          }),
        }
      );

      if (response.ok) {
        const result = await response.json();
        if (onExerciseComplete) {
          onExerciseComplete(result);
        }
      }
    } catch (err) {
      console.error('Error submitting exercise:', err);
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loadingState}>
          <p>Generating your personalized exercise...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.errorState}>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!exercise) {
    return (
      <div className={styles.container}>
        <div className={styles.errorState}>
          <p>Unable to generate exercise. Please try again.</p>
        </div>
      </div>
    );
  }

  // Highlight prompt with color coding
  const promptLines = exercise.text_prompt.split('\n');
  const typedText = keystrokesRef.current;

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.title}>
          <span className={styles.icon}>
            {exercise.exercise_type === 'weak_key_drill' && '🎯'}
            {exercise.exercise_type === 'error_pattern' && '🔧'}
            {exercise.exercise_type === 'speed_challenge' && '⚡'}
            {exercise.exercise_type === 'accuracy_focus' && '🎪'}
            {exercise.exercise_type === 'mixed' && '📝'}
          </span>
          <div>
            <h2>{exercise.description}</h2>
            <p className={styles.focusChars}>
              Focus: {exercise.focus_chars.length > 0 ? exercise.focus_chars.join(', ') : 'General practice'}
            </p>
          </div>
        </div>
        <div className={styles.difficulty}>
          Difficulty {exercise.difficulty}/10
        </div>
      </div>

      {/* Prompt Display */}
      <div className={styles.promptArea}>
        <div className={styles.prompt}>
          {promptLines.map((line, lineIndex) => (
            <div key={lineIndex} className={styles.promptLine}>
              {line.split('').map((char, charIndex) => {
                const globalIndex = promptLines
                  .slice(0, lineIndex)
                  .join('\n').length +
                  (lineIndex > 0 ? lineIndex : 0) +
                  charIndex;

                let charClass = styles.promptChar;

                if (typedText.length > globalIndex) {
                  if (typedText[globalIndex] === char) {
                    charClass += ` ${styles.correct}`;
                  } else {
                    charClass += ` ${styles.incorrect}`;
                  }
                }

                if (typedText.length === globalIndex && isActive) {
                  charClass += ` ${styles.cursor}`;
                }

                return (
                  <span key={charIndex} className={charClass}>
                    {char}
                  </span>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Metrics Display */}
      <div className={styles.metricsBar}>
        <div className={styles.metric}>
          <span className={styles.metricLabel}>Accuracy</span>
          <span className={styles.metricValue}>{Math.round(metrics.accuracy)}%</span>
        </div>
        <div className={styles.metric}>
          <span className={styles.metricLabel}>WPM</span>
          <span className={styles.metricValue}>{metrics.wpm}</span>
        </div>
        <div className={styles.metric}>
          <span className={styles.metricLabel}>Errors</span>
          <span className={styles.metricValue}>{metrics.errors}</span>
        </div>
        <div className={styles.metric}>
          <span className={styles.metricLabel}>Time</span>
          <span className={styles.metricValue}>{metrics.timeElapsed}s</span>
        </div>
        <div className={styles.metric}>
          <span className={styles.metricLabel}>Progress</span>
          <span className={styles.metricValue}>
            {Math.round((metrics.currentCharIndex / exercise.text_prompt.length) * 100)}%
          </span>
        </div>
      </div>

      {/* Input Area */}
      <div className={styles.inputArea}>
        {!isActive ? (
          <button className={styles.startButton} onClick={handleStartExercise}>
            ▶ Start Exercise
          </button>
        ) : (
          <input
            ref={inputRef}
            type="text"
            className={styles.input}
            onKeyDown={handleKeyPress}
            placeholder="Start typing..."
            autoFocus
          />
        )}
      </div>

      {/* Instructions */}
      <div className={styles.instructions}>
        <p>Type the text above. This exercise is personalized to your needs.</p>
        {exercise.focus_chars.length > 0 && (
          <p>
            Pay special attention to: <strong>{exercise.focus_chars.join(', ')}</strong>
          </p>
        )}
      </div>
    </div>
  );
};

export default ExerciseInterface;
