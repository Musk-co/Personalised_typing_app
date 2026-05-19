/**
 * TypingTest Results Component
 * 
 * Displays comprehensive results after a typing test, including:
 * - Overall metrics (WPM, accuracy)
 * - Error analysis and classification
 * - Weak key identification
 * - Performance visualization
 */

import React, { useEffect, useState } from 'react';
import { useTyping } from '@hooks/useTyping';
import ErrorVisualization from './ErrorVisualization';
import styles from './Results.module.css';

interface ResultsProps {
  sessionId: string;
  onRetry?: () => void;
  onExit?: () => void;
}

interface ErrorAnalysis {
  total_errors: number;
  by_type: Record<string, number>;
  levenshtein_distance: number;
}

interface WeakKey {
  character: string;
  attempts: number;
  errors: number;
  error_rate: number;
  error_types: Record<string, number>;
}

interface SessionResults {
  errorAnalysis: ErrorAnalysis;
  weakKeys: WeakKey[];
  perfectKeys: string[];
  totalKeystrokes: number;
}

export const Results: React.FC<ResultsProps> = ({ sessionId, onRetry, onExit }) => {
  const { currentSession } = useTyping();
  const [results, setResults] = useState<SessionResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch results from backend
   */
  useEffect(() => {
    const fetchResults = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch error analysis
        const analysisResponse = await fetch(
          `/api/v1/sessions/${sessionId}/keystrokes/analysis`
        );

        if (!analysisResponse.ok) {
          throw new Error('Failed to fetch error analysis');
        }

        const analysisData = await analysisResponse.json();

        // Fetch weak keys
        const weakKeysResponse = await fetch(
          `/api/v1/sessions/${sessionId}/weak-keys`
        );

        if (!weakKeysResponse.ok) {
          throw new Error('Failed to fetch weak keys');
        }

        const weakKeysData = await weakKeysResponse.json();

        setResults({
          errorAnalysis: analysisData.error_classification,
          weakKeys: weakKeysData.weak_keys,
          perfectKeys: weakKeysData.perfect_keys,
          totalKeystrokes: analysisData.total_keystrokes,
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Error fetching results:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [sessionId]);

  if (loading) {
    return (
      <div className={styles.resultsContainer}>
        <div className={styles.loadingState}>
          <div className={styles.spinner} />
          <p>Analyzing your typing performance...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.resultsContainer}>
        <div className={styles.errorState}>
          <h2>Error Loading Results</h2>
          <p>{error}</p>
          <button onClick={onExit} className={styles.buttonPrimary}>
            Exit
          </button>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className={styles.resultsContainer}>
        <div className={styles.emptyState}>
          <h2>No Results Available</h2>
          <p>No typing data was captured for this session.</p>
        </div>
      </div>
    );
  }

  const accuracy =
    results.totalKeystrokes > 0
      ? (
          ((results.totalKeystrokes - results.errorAnalysis.total_errors) /
            results.totalKeystrokes) *
          100
        ).toFixed(2)
      : '0';

  return (
    <div className={styles.resultsContainer}>
      {/* Header */}
      <div className={styles.header}>
        <h1>Test Complete!</h1>
        <p>Here's how you performed</p>
      </div>

      {/* Summary Metrics */}
      <div className={styles.summaryMetrics}>
        <div className={styles.metricCard}>
          <div className={styles.metricTitle}>Accuracy</div>
          <div className={styles.metricValue}>{accuracy}%</div>
          <div className={styles.metricSubtitle}>
            {results.errorAnalysis.total_errors} errors out of{' '}
            {results.totalKeystrokes}
          </div>
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricTitle}>Levenshtein Distance</div>
          <div className={styles.metricValue}>
            {results.errorAnalysis.levenshtein_distance}
          </div>
          <div className={styles.metricSubtitle}>Edit distance</div>
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricTitle}>Total Keystrokes</div>
          <div className={styles.metricValue}>{results.totalKeystrokes}</div>
          <div className={styles.metricSubtitle}>Captured and analyzed</div>
        </div>

        {Object.entries(results.errorAnalysis.by_type).length > 0 && (
          <div className={styles.metricCard}>
            <div className={styles.metricTitle}>Most Common Error</div>
            <div className={styles.metricValue}>
              {
                Object.entries(results.errorAnalysis.by_type).sort(
                  ([, a], [, b]) => b - a
                )[0][0]
              }
            </div>
            <div className={styles.metricSubtitle}>
              {
                Object.entries(results.errorAnalysis.by_type).sort(
                  ([, a], [, b]) => b - a
                )[0][1]
              }{' '}
              occurrences
            </div>
          </div>
        )}
      </div>

      {/* Detailed Error Visualization */}
      {results.weakKeys.length > 0 || results.errorAnalysis.total_errors > 0 ? (
        <ErrorVisualization
          errorDetails={{}}
          errorClassification={results.errorAnalysis}
          weakKeys={results.weakKeys.map((k) => k.character)}
          keyStats={Object.fromEntries(
            results.weakKeys.map((k) => [
              k.character,
              {
                errors: k.errors,
                attempts: k.attempts,
                error_rate: k.error_rate,
              },
            ])
          )}
          characterClassification={{}}
        />
      ) : (
        <div className={styles.perfectScore}>
          <div className={styles.perfectIcon}>🎉</div>
          <h2>Perfect Score!</h2>
          <p>You typed every character correctly without any errors.</p>
        </div>
      )}

      {/* Perfect Keys Section */}
      {results.perfectKeys.length > 0 && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Perfect Keys</h3>
          <div className={styles.perfectKeysList}>
            {results.perfectKeys.map((key) => (
              <span key={key} className={styles.perfectKey}>
                {key === ' ' ? '⎵' : key}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className={styles.actions}>
        {onRetry && (
          <button onClick={onRetry} className={styles.buttonSecondary}>
            Retry Test
          </button>
        )}
        {onExit && (
          <button onClick={onExit} className={styles.buttonPrimary}>
            Back to Dashboard
          </button>
        )}
      </div>

      {/* Insights */}
      <div className={styles.insights}>
        <h3>Key Insights</h3>
        <ul>
          {results.weakKeys.length > 0 && (
            <li>
              Your weakest key is <strong>{results.weakKeys[0].character}</strong> with{' '}
              {(results.weakKeys[0].error_rate * 100).toFixed(0)}% error rate. Consider
              practicing this key more.
            </li>
          )}
          {results.errorAnalysis.total_errors === 0 && (
            <li>
              <strong>Flawless execution!</strong> You achieved 100% accuracy. Keep up the
              great work!
            </li>
          )}
          {results.perfectKeys.length >= 20 && (
            <li>
              You have <strong>{results.perfectKeys.length} perfect keys</strong>. Focus on
              improving the remaining ones.
            </li>
          )}
        </ul>
      </div>
    </div>
  );
};

export default Results;
