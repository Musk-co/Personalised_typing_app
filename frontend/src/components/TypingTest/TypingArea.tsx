/**
 * TypingArea Component
 * 
 * The main typing interface. Captures every keystroke with precision timing.
 * Displays visual feedback for correct/incorrect characters in real-time.
 * 
 * Features:
 * - Character-level classification (correct/incorrect/pending)
 * - Real-time WPM and accuracy calculation
 * - Error detection and visual feedback
 * - Keystroke event logging (for detailed analysis)
 * - Focused cursor with smooth animation
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useTyping } from '@hooks/useTyping';
import styles from './TypingArea.module.css';

interface KeystrokeEvent {
  character: string;
  position: number;
  timestamp_ms: number;
  expected_char: string;
}

interface CharacterStatus {
  status: 'correct' | 'incorrect' | 'pending' | 'extra';
  expected: string;
  actual?: string;
}

export const TypingArea: React.FC = () => {
  const {
    testText,
    typedText,
    isRunning,
    startTest,
    stopTest,
    addCharacter,
    removeCharacter,
    calculateMetrics,
    currentSession,
  } = useTyping();

  const [keystrokeEvents, setKeystrokeEvents] = useState<KeystrokeEvent[]>([]);
  const [focusedCharIndex, setFocusedCharIndex] = useState<number>(0);
  const [realTimeWpm, setRealTimeWpm] = useState<number>(0);
  const [realTimeAccuracy, setRealTimeAccuracy] = useState<number>(0);
  const [characterStatuses, setCharacterStatuses] = useState<CharacterStatus[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const startTimeRef = useRef<number | null>(null);
  const metricsIntervalRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Classify each character as correct, incorrect, or pending
   */
  const classifyCharacters = useCallback((): CharacterStatus[] => {
    const statuses: CharacterStatus[] = [];

    // Typed characters
    for (let i = 0; i < typedText.length; i++) {
      const typedChar = typedText[i];
      const expectedChar = testText[i] || '';

      if (i < testText.length) {
        statuses[i] = {
          status: typedChar === expectedChar ? 'correct' : 'incorrect',
          expected: expectedChar,
          actual: typedChar,
        };
      } else {
        // Extra characters typed
        statuses[i] = {
          status: 'extra',
          expected: '',
          actual: typedChar,
        };
      }
    }

    // Pending characters (not yet typed)
    for (let i = typedText.length; i < testText.length; i++) {
      statuses[i] = {
        status: 'pending',
        expected: testText[i],
      };
    }

    return statuses;
  }, [typedText, testText]);

  /**
   * Update real-time WPM and accuracy
   */
  const updateMetrics = useCallback(() => {
    if (!isRunning || !startTimeRef.current || typedText.length === 0) {
      return;
    }

    const elapsedMs = Date.now() - startTimeRef.current;
    const elapsedMinutes = elapsedMs / 60000;

    // WPM: characters / 5 / minutes
    const wpm = (typedText.length / 5) / elapsedMinutes;
    setRealTimeWpm(Math.round(wpm * 100) / 100);

    // Accuracy: correct characters / expected characters * 100
    let correctChars = 0;
    for (let i = 0; i < Math.min(typedText.length, testText.length); i++) {
      if (typedText[i] === testText[i]) {
        correctChars++;
      }
    }
    const accuracy = (correctChars / testText.length) * 100;
    setRealTimeAccuracy(Math.round(accuracy * 100) / 100);
  }, [isRunning, typedText, testText]);

  /**
   * Handle keystroke input
   */
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (!isRunning) {
        return;
      }

      const key = e.key;
      const timestamp = Date.now() - (startTimeRef.current || Date.now());

      // Track keystroke event
      const event: KeystrokeEvent = {
        character: key,
        position: typedText.length,
        timestamp_ms: timestamp,
        expected_char: testText[typedText.length] || '',
      };

      setKeystrokeEvents((prev) => [...prev, event]);

      // Handle special keys
      if (key === 'Backspace') {
        e.preventDefault();
        removeCharacter();
        setFocusedCharIndex(Math.max(0, focusedCharIndex - 1));
      } else if (key.length === 1 && key !== ' ' && /[\S]/.test(key)) {
        // Regular character
        e.preventDefault();
        addCharacter(key);
        setFocusedCharIndex(typedText.length + 1);
      } else if (key === ' ') {
        // Space is allowed
        e.preventDefault();
        addCharacter(' ');
        setFocusedCharIndex(typedText.length + 1);
      }
    },
    [isRunning, typedText, testText, focusedCharIndex, addCharacter, removeCharacter]
  );

  /**
   * Initialize test
   */
  const handleStartTest = () => {
    setKeystrokeEvents([]);
    setCharacterStatuses([]);
    setFocusedCharIndex(0);
    setRealTimeWpm(0);
    setRealTimeAccuracy(0);
    startTimeRef.current = Date.now();
    startTest();
    inputRef.current?.focus();
  };

  /**
   * Submit keystroke batch to backend for analysis
   */
  const submitKeystrokeBatch = useCallback(async () => {
    if (!currentSession?.id || keystrokeEvents.length === 0) {
      return;
    }

    try {
      const batch = {
        events: keystrokeEvents.map((event) => ({
          char: event.character,
          timestamp: event.timestamp_ms,
          position: event.position,
          expected: event.expected_char,
          is_correct: event.character === event.expected_char,
          elapsed_ms: event.timestamp_ms,
        })),
        context: `Difficulty ${currentSession.difficulty_level}`,
        test_duration_ms: Date.now() - (startTimeRef.current || 0),
      };

      const response = await fetch(
        `/api/v1/sessions/${currentSession.id}/keystrokes`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(batch),
        }
      );

      if (!response.ok) {
        console.error('Failed to submit keystroke batch:', response.statusText);
        return;
      }

      const result = await response.json();
      console.log('Keystroke batch submitted:', result);
    } catch (error) {
      console.error('Error submitting keystroke batch:', error);
    }
  }, [keystrokeEvents, currentSession?.id]);

  /**
   * End test
   */
  const handleStopTest = useCallback(() => {
    if (metricsIntervalRef.current) {
      clearInterval(metricsIntervalRef.current);
    }
    // Submit keystroke data to backend
    submitKeystrokeBatch();
    stopTest();
  }, [submitKeystrokeBatch, stopTest]);

  /**
   * Calculate metrics on component mount/update
   */
  useEffect(() => {
    if (isRunning && startTimeRef.current) {
      metricsIntervalRef.current = setInterval(() => {
        updateMetrics();
      }, 100);

      return () => {
        if (metricsIntervalRef.current) {
          clearInterval(metricsIntervalRef.current);
        }
      };
    }
  }, [isRunning, typedText, testText, updateMetrics]);

  /**
   * Update character classifications
   */
  useEffect(() => {
    const statuses = classifyCharacters();
    setCharacterStatuses(statuses);
  }, [typedText, classifyCharacters]);

  /**
   * Auto-stop when test text is fully typed
   */
  useEffect(() => {
    if (isRunning && typedText.length >= testText.length && testText.length > 0) {
      handleStopTest();
    }
  }, [isRunning, typedText, testText]);

  return (
    <div className={styles.typingAreaContainer}>
      {/* Header with test info */}
      <div className={styles.header}>
        <h2>Typing Test - Difficulty {currentSession?.difficulty_level || 1}</h2>
        <div className={styles.statusBadge}>
          {isRunning ? (
            <span className={styles.statusActive}>● Running</span>
          ) : typedText.length > 0 ? (
            <span className={styles.statusCompleted}>✓ Completed</span>
          ) : (
            <span className={styles.statusIdle}>Ready to start</span>
          )}
        </div>
      </div>

      {/* Display text with character-level feedback */}
      <div className={styles.textDisplayBox}>
        <div className={styles.textContainer}>
          {testText.split('').map((char, index) => {
            const status = characterStatuses[index];
            const isCurrentPosition = index === typedText.length;
            const classNames = [styles.char];

            if (status) {
              classNames.push(styles[status.status]);
            }
            if (isCurrentPosition) {
              classNames.push(styles.current);
            }

            return (
              <span key={index} className={classNames.join(' ')}>
                {char === ' ' ? '·' : char}
              </span>
            );
          })}

          {/* Cursor */}
          {isRunning && (
            <span className={styles.cursor}>|</span>
          )}
        </div>

        {/* Progress bar */}
        <div className={styles.progressBar}>
          <div
            className={styles.progress}
            style={{
              width: `${(typedText.length / testText.length) * 100}%`,
            }}
          />
        </div>
      </div>

      {/* Live metrics display */}
      <div className={styles.metricsRow}>
        <div className={styles.metric}>
          <span className={styles.metricLabel}>WPM</span>
          <span className={styles.metricValue}>{realTimeWpm}</span>
        </div>
        <div className={styles.metric}>
          <span className={styles.metricLabel}>Accuracy</span>
          <span className={styles.metricValue}>{realTimeAccuracy}%</span>
        </div>
        <div className={styles.metric}>
          <span className={styles.metricLabel}>Typed</span>
          <span className={styles.metricValue}>
            {typedText.length}/{testText.length}
          </span>
        </div>
        <div className={styles.metric}>
          <span className={styles.metricLabel}>Errors</span>
          <span className={styles.metricValue}>
            {typedText.length > 0
              ? characterStatuses.filter((s) => s.status === 'incorrect' || s.status === 'extra').length
              : 0}
          </span>
        </div>
      </div>

      {/* Hidden input for capturing keystrokes */}
      <input
        ref={inputRef}
        type="text"
        className={styles.hiddenInput}
        value={typedText}
        onChange={() => {}} // Controlled by onKeyDown
        onKeyDown={handleKeyDown}
        placeholder="Click here or start typing..."
        disabled={!isRunning}
        autoComplete="off"
        spellCheck="false"
      />

      {/* Control buttons */}
      <div className={styles.controls}>
        {!isRunning ? (
          <button onClick={handleStartTest} className={styles.buttonStart}>
            Start Test
          </button>
        ) : (
          <button onClick={handleStopTest} className={styles.buttonStop}>
            Stop Test
          </button>
        )}
      </div>

      {/* Character legend */}
      <div className={styles.legend}>
        <div className={styles.legendItem}>
          <span className={`${styles.char} ${styles.correct}`}>a</span>
          <span>Correct</span>
        </div>
        <div className={styles.legendItem}>
          <span className={`${styles.char} ${styles.incorrect}`}>a</span>
          <span>Incorrect</span>
        </div>
        <div className={styles.legendItem}>
          <span className={`${styles.char} ${styles.pending}`}>a</span>
          <span>Pending</span>
        </div>
        <div className={styles.legendItem}>
          <span className={`${styles.char} ${styles.extra}`}>a</span>
          <span>Extra</span>
        </div>
      </div>
    </div>
  );
};

export default TypingArea;
