/**
 * Stats Panel Component
 *
 * Displays real-time session statistics with live updates.
 * Shows metrics as they happen - WPM, accuracy, errors, time.
 */

import React, { useEffect, useState } from 'react';
import styles from './StatsPanel.module.css';

interface SessionStats {
  wpm: number;
  accuracy: number;
  errors: number;
  duration_seconds: number;
  characters_typed: number;
  consistency: number;
}

interface StatsPanelProps {
  stats: SessionStats;
  isActive?: boolean;
  showDetails?: boolean;
}

export const StatsPanel: React.FC<StatsPanelProps> = ({
  stats,
  isActive = false,
  showDetails = true,
}) => {
  const [displayWpm, setDisplayWpm] = useState(stats.wpm);
  const [displayAccuracy, setDisplayAccuracy] = useState(stats.accuracy);
  const [prevWpm, setPrevWpm] = useState(stats.wpm);
  const [prevAccuracy, setPrevAccuracy] = useState(stats.accuracy);

  // Animate stat changes
  useEffect(() => {
    if (stats.wpm !== prevWpm) {
      setPrevWpm(stats.wpm);
      // Animate WPM change
      const diff = stats.wpm - displayWpm;
      const steps = 10;
      const increment = diff / steps;
      let current = 0;

      const interval = setInterval(() => {
        if (current < steps) {
          setDisplayWpm((prev) => prev + increment);
          current++;
        } else {
          setDisplayWpm(stats.wpm);
          clearInterval(interval);
        }
      }, 20);

      return () => clearInterval(interval);
    }
  }, [stats.wpm]);

  useEffect(() => {
    if (stats.accuracy !== prevAccuracy) {
      setPrevAccuracy(stats.accuracy);
      // Animate accuracy change
      const diff = stats.accuracy - displayAccuracy;
      const steps = 10;
      const increment = diff / steps;
      let current = 0;

      const interval = setInterval(() => {
        if (current < steps) {
          setDisplayAccuracy((prev) => prev + increment);
          current++;
        } else {
          setDisplayAccuracy(stats.accuracy);
          clearInterval(interval);
        }
      }, 20);

      return () => clearInterval(interval);
    }
  }, [stats.accuracy]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getWpmColor = (wpm: number) => {
    if (wpm < 10) return '#EF4444'; // Red
    if (wpm < 25) return '#F59E0B'; // Orange
    if (wpm < 50) return '#EAB308'; // Yellow
    if (wpm < 75) return '#84CC16'; // Lime
    return '#10B981'; // Green
  };

  const getAccuracyColor = (accuracy: number) => {
    if (accuracy < 80) return '#EF4444'; // Red
    if (accuracy < 90) return '#F59E0B'; // Orange
    if (accuracy < 95) return '#EAB308'; // Yellow
    if (accuracy < 98) return '#84CC16'; // Lime
    return '#10B981'; // Green
  };

  const accuracyClass =
    stats.accuracy >= 98
      ? styles.excellent
      : stats.accuracy >= 95
        ? styles.great
        : stats.accuracy >= 90
          ? styles.good
          : stats.accuracy >= 80
            ? styles.fair
            : styles.poor;

  const wpmClass =
    stats.wpm >= 75
      ? styles.excellent
      : stats.wpm >= 50
        ? styles.great
        : stats.wpm >= 25
          ? styles.good
          : styles.poor;

  return (
    <div className={`${styles.container} ${isActive ? styles.active : ''}`}>
      {/* Primary Stats (WPM and Accuracy) */}
      <div className={styles.primaryStats}>
        {/* WPM */}
        <div className={styles.statBlock}>
          <div className={styles.statLabel}>WPM</div>
          <div className={`${styles.statValue} ${wpmClass}`} style={{ color: getWpmColor(stats.wpm) }}>
            {displayWpm.toFixed(1)}
          </div>
          <div className={styles.statUnit}>words/min</div>
        </div>

        {/* Accuracy */}
        <div className={styles.statBlock}>
          <div className={styles.statLabel}>Accuracy</div>
          <div className={`${styles.statValue} ${accuracyClass}`} style={{ color: getAccuracyColor(stats.accuracy) }}>
            {displayAccuracy.toFixed(1)}%
          </div>
          <div className={styles.statUnit}>correct</div>
        </div>

        {/* Errors */}
        <div className={styles.statBlock}>
          <div className={styles.statLabel}>Errors</div>
          <div className={styles.statValue} style={{ color: stats.errors > 0 ? '#EF4444' : '#10B981' }}>
            {stats.errors}
          </div>
          <div className={styles.statUnit}>mistakes</div>
        </div>

        {/* Time */}
        <div className={styles.statBlock}>
          <div className={styles.statLabel}>Time</div>
          <div className={styles.statValue}>{formatTime(stats.duration_seconds)}</div>
          <div className={styles.statUnit}>elapsed</div>
        </div>
      </div>

      {/* Secondary Stats (if showDetails) */}
      {showDetails && (
        <div className={styles.secondaryStats}>
          {/* Characters Typed */}
          <div className={styles.secondaryStat}>
            <span className={styles.secondaryLabel}>Characters:</span>
            <span className={styles.secondaryValue}>{stats.characters_typed}</span>
          </div>

          {/* Consistency */}
          <div className={styles.secondaryStat}>
            <span className={styles.secondaryLabel}>Consistency:</span>
            <span className={styles.secondaryValue}>{stats.consistency.toFixed(0)}</span>
          </div>

          {/* Progress Bar (if duration tracked) */}
          {stats.duration_seconds > 0 && (
            <div className={styles.progressSection}>
              <div className={styles.progressLabel}>Session Progress</div>
              <div className={styles.progressBar}>
                <div
                  className={styles.progressFill}
                  style={{
                    width: `${Math.min((stats.duration_seconds / 120) * 100, 100)}%`,
                  }}
                ></div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Status Indicator */}
      {isActive && (
        <div className={styles.activeIndicator}>
          <span className={styles.pulse}></span>
          Typing...
        </div>
      )}
    </div>
  );
};

export default StatsPanel;
