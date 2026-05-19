/**
 * ErrorVisualization Component
 * 
 * Displays detailed error patterns and classification visually.
 * Shows:
 * - Error timeline
 * - Weak keys (keys with high error rates)
 * - Error type breakdown (substitution, insertion, deletion, transposition)
 * - Per-character error details
 */

import React, { useMemo } from 'react';
import styles from './ErrorVisualization.module.css';

interface ErrorDetail {
  position: number;
  expected: string;
  actual: string;
  error_type: string;
  timestamp_ms: number;
  context: string;
}

interface ErrorVisualizationProps {
  errorDetails: Record<string, ErrorDetail>;
  errorClassification: {
    total: number;
    by_type: Record<string, number>;
    levenshtein_distance: number;
  };
  weakKeys: string[];
  keyStats: Record<string, any>;
  characterClassification: Record<string, any>;
}

export const ErrorVisualization: React.FC<ErrorVisualizationProps> = ({
  errorDetails,
  errorClassification,
  weakKeys,
  keyStats,
  characterClassification,
}) => {
  // Get error timeline (sorted by position)
  const errorTimeline = useMemo(() => {
    return Object.entries(errorDetails)
      .map(([_, error]) => error)
      .sort((a, b) => a.position - b.position);
  }, [errorDetails]);

  // Calculate error type percentages
  const errorTypePercentages = useMemo(() => {
    const total = errorClassification.total || 1;
    return Object.entries(errorClassification.by_type).reduce(
      (acc, [type, count]) => {
        acc[type] = Math.round((count / total) * 100);
        return acc;
      },
      {} as Record<string, number>
    );
  }, [errorClassification]);

  // Get top weak keys (highest error rate)
  const topWeakKeys = weakKeys.slice(0, 5);

  return (
    <div className={styles.errorVisualizationContainer}>
      {/* Summary Stats */}
      <div className={styles.summarySection}>
        <div className={styles.summaryCard}>
          <span className={styles.label}>Total Errors</span>
          <span className={styles.value}>{errorClassification.total}</span>
        </div>
        <div className={styles.summaryCard}>
          <span className={styles.label}>Levenshtein Distance</span>
          <span className={styles.value}>{errorClassification.levenshtein_distance}</span>
        </div>
      </div>

      {/* Error Type Breakdown */}
      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>Error Type Breakdown</h3>
        <div className={styles.errorTypesGrid}>
          {Object.entries(errorTypePercentages).map(([type, percentage]) => (
            <div key={type} className={styles.errorTypeCard}>
              <div className={styles.errorTypeName}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </div>
              <div className={styles.errorTypeBarContainer}>
                <div
                  className={`${styles.errorTypeBar} ${styles[type]}`}
                  style={{ width: `${percentage}%` }}
                />
              </div>
              <div className={styles.errorTypeCount}>
                {errorClassification.by_type[type] || 0}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Weak Keys Heatmap */}
      {topWeakKeys.length > 0 && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Weak Keys (Top 5)</h3>
          <div className={styles.weakKeysContainer}>
            {topWeakKeys.map((key) => {
              const stats = keyStats[key] || {};
              const errorRate = stats.error_rate || 0;
              const intensity = Math.round(errorRate * 100);

              return (
                <div
                  key={key}
                  className={styles.keyHeatmap}
                  style={{
                    backgroundColor: `rgba(231, 76, 60, ${errorRate})`,
                  }}
                  title={`${key}: ${stats.errors}/${stats.attempts} errors`}
                >
                  <span className={styles.keyChar}>{key === ' ' ? '⎵' : key}</span>
                  <span className={styles.errorIntensity}>{intensity}%</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Error Timeline */}
      {errorTimeline.length > 0 && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Error Timeline</h3>
          <div className={styles.timelineContainer}>
            {errorTimeline.slice(0, 10).map((error, index) => (
              <div key={index} className={styles.timelineItem}>
                <div className={styles.timelineMarker}>
                  <span className={styles.position}>{error.position}</span>
                </div>
                <div className={styles.timelineContent}>
                  <div className={styles.errorDescription}>
                    <span className={styles.expected}>
                      Expected: <code>{error.expected}</code>
                    </span>
                    <span className={styles.actual}>
                      Typed: <code>{error.actual}</code>
                    </span>
                    <span className={`${styles.errorType} ${styles[error.error_type]}`}>
                      {error.error_type}
                    </span>
                  </div>
                  <div className={styles.context}>{error.context}</div>
                  <div className={styles.timestamp}>
                    {(error.timestamp_ms / 1000).toFixed(2)}s
                  </div>
                </div>
              </div>
            ))}
            {errorTimeline.length > 10 && (
              <div className={styles.moreIndicator}>
                +{errorTimeline.length - 10} more errors
              </div>
            )}
          </div>
        </div>
      )}

      {/* Error-Free Keys */}
      {Object.keys(keyStats).length > 0 && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Perfect Keys (No Errors)</h3>
          <div className={styles.perfectKeysContainer}>
            {Object.entries(keyStats)
              .filter(([_, stats]) => stats.errors === 0)
              .slice(0, 20)
              .map(([key, stats]) => (
                <div key={key} className={styles.perfectKeyBadge}>
                  {key === ' ' ? '⎵' : key}
                  <span className={styles.badge}>{stats.attempts}</span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ErrorVisualization;
