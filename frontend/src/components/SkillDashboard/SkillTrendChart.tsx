/**
 * Skill Trend Chart Component
 * 
 * Visualizes WPM and accuracy progression over time.
 * Shows historical data points, trends, and milestones.
 * Helps users see "where was I weeks ago vs now"
 */

import React, { useEffect, useState } from 'react';
import styles from './SkillTrendChart.module.css';

interface DataPoint {
  session_id: number;
  wpm: number;
  accuracy: number;
  cumulative_wpm_avg: number;
  cumulative_accuracy_avg: number;
  snapshot_date: string;
}

interface SkillHistory {
  user_id: number;
  period_days: number;
  history: DataPoint[];
  overall_trend: string;
  current_momentum: number;
}

interface SkillTrendChartProps {
  userId: number;
  days?: number;
}

export const SkillTrendChart: React.FC<SkillTrendChartProps> = ({ userId, days = 30 }) => {
  const [history, setHistory] = useState<SkillHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMetric, setSelectedMetric] = useState<'wpm' | 'accuracy'>('wpm');

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `/api/v1/users/${userId}/skill-history?days=${days}`
        );

        if (!response.ok) {
          if (response.status === 404) {
            setError('No history data yet. Complete more sessions to see trends.');
            return;
          }
          throw new Error('Failed to fetch history');
        }

        const data = await response.json();
        setHistory(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Error fetching history:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [userId, days]);

  if (loading) {
    return (
      <div className={styles.chartContainer}>
        <div className={styles.loadingState}>
          <p>Loading trends...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.chartContainer}>
        <div className={styles.errorState}>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!history || history.history.length === 0) {
    return (
      <div className={styles.chartContainer}>
        <div className={styles.emptyState}>
          <p>No data yet. Complete typing sessions to see your trends.</p>
        </div>
      </div>
    );
  }

  // Calculate chart dimensions and scales
  const chartWidth = 600;
  const chartHeight = 300;
  const padding = { top: 20, right: 20, bottom: 40, left: 60 };

  const data = history.history;
  const isWPM = selectedMetric === 'wpm';
  const values = isWPM
    ? data.map(d => d.cumulative_wpm_avg)
    : data.map(d => d.cumulative_accuracy_avg);

  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const range = maxValue - minValue || 1;

  // Scale functions
  const xScale = (index: number) =>
    padding.left + (index / (data.length - 1 || 1)) * (chartWidth - padding.left - padding.right);
  const yScale = (value: number) =>
    chartHeight -
    padding.bottom -
    ((value - minValue) / range) * (chartHeight - padding.top - padding.bottom);

  // Generate path for line chart
  const pathPoints = values.map((v, i) => `${xScale(i)},${yScale(v)}`).join('L');
  const linePath = `M${pathPoints}`;

  // Format date
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  // Y-axis labels
  const yAxisSteps = 5;
  const step = range / yAxisSteps;

  return (
    <div className={styles.chartContainer}>
      {/* Header */}
      <div className={styles.chartHeader}>
        <h3 className={styles.chartTitle}>
          {isWPM ? '⚡ Typing Speed' : '🎯 Accuracy'} Progression
        </h3>
        <div className={styles.trendBadge}>
          <span className={styles.trendLabel}>Trend:</span>
          <span className={`${styles.trend} ${styles[history.overall_trend]}`}>
            {history.overall_trend === 'improving' && '↗️ Improving'}
            {history.overall_trend === 'declining' && '↘️ Declining'}
            {history.overall_trend === 'stable' && '→ Stable'}
          </span>
        </div>
      </div>

      {/* Controls */}
      <div className={styles.controls}>
        <button
          className={`${styles.metricButton} ${isWPM ? styles.active : ''}`}
          onClick={() => setSelectedMetric('wpm')}
        >
          WPM
        </button>
        <button
          className={`${styles.metricButton} ${!isWPM ? styles.active : ''}`}
          onClick={() => setSelectedMetric('accuracy')}
        >
          Accuracy
        </button>
      </div>

      {/* Chart */}
      <svg
        viewBox={`0 0 ${chartWidth} ${chartHeight}`}
        className={styles.svg}
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Grid lines */}
        {Array.from({ length: yAxisSteps + 1 }).map((_, i) => {
          const y = yScale(minValue + step * i);
          return (
            <line
              key={`grid-${i}`}
              x1={padding.left}
              y1={y}
              x2={chartWidth - padding.right}
              y2={y}
              stroke="#e2e8f0"
              strokeWidth="1"
              strokeDasharray="4"
            />
          );
        })}

        {/* Y-axis labels */}
        {Array.from({ length: yAxisSteps + 1 }).map((_, i) => {
          const value = minValue + step * i;
          const y = yScale(value);
          return (
            <text
              key={`y-label-${i}`}
              x={padding.left - 10}
              y={y + 4}
              textAnchor="end"
              fontSize="12"
              fill="#718096"
            >
              {isWPM ? value.toFixed(0) : value.toFixed(0) + '%'}
            </text>
          );
        })}

        {/* X-axis */}
        <line
          x1={padding.left}
          y1={chartHeight - padding.bottom}
          x2={chartWidth - padding.right}
          y2={chartHeight - padding.bottom}
          stroke="#cbd5e0"
          strokeWidth="2"
        />

        {/* Y-axis */}
        <line
          x1={padding.left}
          y1={padding.top}
          x2={padding.left}
          y2={chartHeight - padding.bottom}
          stroke="#cbd5e0"
          strokeWidth="2"
        />

        {/* Data points and line */}
        <path
          d={linePath}
          fill="none"
          stroke={isWPM ? '#4299e1' : '#38a169'}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Data points circles */}
        {values.map((v, i) => (
          <circle
            key={`point-${i}`}
            cx={xScale(i)}
            cy={yScale(v)}
            r="4"
            fill={isWPM ? '#4299e1' : '#38a169'}
            opacity="0.8"
            className={styles.dataPoint}
          >
            <title>
              {formatDate(data[i].snapshot_date)}: {v.toFixed(1)}
              {isWPM ? ' WPM' : '%'}
            </title>
          </circle>
        ))}

        {/* X-axis labels (sample) */}
        {data.map((d, i) => {
          if (i % Math.ceil(data.length / 5) === 0 || i === data.length - 1) {
            return (
              <text
                key={`x-label-${i}`}
                x={xScale(i)}
                y={chartHeight - 10}
                textAnchor="middle"
                fontSize="12"
                fill="#718096"
              >
                {formatDate(d.snapshot_date)}
              </text>
            );
          }
          return null;
        })}
      </svg>

      {/* Statistics */}
      <div className={styles.statistics}>
        <div className={styles.statItem}>
          <div className={styles.statLabel}>Current</div>
          <div className={styles.statValue}>
            {isWPM
              ? values[values.length - 1].toFixed(1)
              : values[values.length - 1].toFixed(1) + '%'}
          </div>
        </div>

        <div className={styles.statItem}>
          <div className={styles.statLabel}>Best</div>
          <div className={styles.statValue}>
            {isWPM ? maxValue.toFixed(1) : maxValue.toFixed(1) + '%'}
          </div>
        </div>

        <div className={styles.statItem}>
          <div className={styles.statLabel}>Average</div>
          <div className={styles.statValue}>
            {isWPM
              ? (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1)
              : ((values.reduce((a, b) => a + b, 0) / values.length).toFixed(1) + '%')}
          </div>
        </div>

        {history.current_momentum !== 0 && (
          <div className={styles.statItem}>
            <div className={styles.statLabel}>Momentum</div>
            <div className={`${styles.statValue} ${history.current_momentum > 0 ? styles.positive : styles.negative}`}>
              {history.current_momentum > 0 ? '+' : ''}{history.current_momentum.toFixed(2)}
            </div>
          </div>
        )}
      </div>

      {/* Insights */}
      <div className={styles.insight}>
        <p>
          {history.overall_trend === 'improving'
            ? isWPM
              ? 'Your speed is steadily improving! Keep the momentum going.'
              : 'Your accuracy is getting better. Consistency is key!'
            : history.overall_trend === 'declining'
            ? 'Your performance has dipped. Take a break and come back fresh.'
            : isWPM
            ? "You're holding steady on speed. Ready for a challenge?"
            : "You're maintaining solid accuracy. Build your speed next."}
        </p>
      </div>
    </div>
  );
};

export default SkillTrendChart;
