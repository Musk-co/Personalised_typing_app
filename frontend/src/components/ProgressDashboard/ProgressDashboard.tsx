/**
 * Progress Dashboard
 *
 * Comprehensive display of user's learning journey with trend visualization,
 * achievements, streaks, and keyboard heatmaps.
 *
 * The feeling: "I'm actually getting better, and I can see it."
 */

import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import styles from './ProgressDashboard.module.css';

interface ProgressStats {
  skill_profile: {
    avg_wpm: number;
    avg_accuracy: number;
    best_wpm: number | null;
    best_accuracy: number | null;
    consistency_score: number;
    total_sessions: number;
    total_keystrokes: number;
    improvement_week: number | null;
    improvement_month: number | null;
  };
  achievements: Achievement[];
  streaks: Streak[];
  recent_milestones: Milestone[];
  progress_trend: TrendData[];
}

interface Achievement {
  type: string;
  title: string;
  description: string;
  rarity: string;
  icon: string | null;
  earned_at: string;
}

interface Streak {
  type: string;
  current_count: number;
  longest_count: number;
  last_activity_date: string | null;
}

interface Milestone {
  type: string;
  title: string;
  description: string;
  metric_name: string | null;
  metric_value: number | null;
  achieved_at: string;
  celebration_shown: boolean;
}

interface TrendData {
  date: string;
  avg_wpm: number;
  avg_accuracy: number;
  best_wpm: number | null;
  best_accuracy: number | null;
  total_sessions: number;
  week_improvement: number | null;
  month_improvement: number | null;
}

interface KeyboardHeatmap {
  heatmap: {
    [char: string]: {
      error_rate: number;
      color: string;
    };
  };
  generated_at: string;
}

export const ProgressDashboard: React.FC<{ userId: number }> = ({ userId }) => {
  const [stats, setStats] = useState<ProgressStats | null>(null);
  const [heatmap, setHeatmap] = useState<KeyboardHeatmap | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'trends' | 'achievements' | 'heatmap'>('overview');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [statsRes, heatmapRes] = await Promise.all([
          fetch(`/api/v1/users/${userId}/progress/stats`),
          fetch(`/api/v1/users/${userId}/keyboard-heatmap`),
        ]);

        if (!statsRes.ok || !heatmapRes.ok) {
          throw new Error('Failed to fetch progress data');
        }

        const statsData = await statsRes.json();
        const heatmapData = await heatmapRes.json();

        setStats(statsData);
        setHeatmap(heatmapData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    // Refresh every 5 minutes
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [userId]);

  if (loading) {
    return <div className={styles.container}><div className={styles.loading}>Loading your progress...</div></div>;
  }

  if (error || !stats) {
    return <div className={styles.container}><div className={styles.error}>{error || 'Failed to load progress'}</div></div>;
  }

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'legendary': return '#FFD700';
      case 'epic': return '#9333EA';
      case 'rare': return '#3B82F6';
      default: return '#6B7280';
    }
  };

  const getStreakEmoji = (type: string) => {
    switch (type) {
      case 'days_practiced': return '🔥';
      case 'error_free_sessions': return '⭐';
      default: return '🎯';
    }
  };

  return (
    <div className={styles.container}>
      {/* Header with Summary Stats */}
      <div className={styles.header}>
        <h1>Your Progress 📈</h1>
        <p className={styles.subheader}>Your learning journey at a glance</p>
      </div>

      {/* Summary Stats Grid */}
      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statIcon}>⚡</div>
          <div className={styles.statValue}>{stats.skill_profile.avg_wpm.toFixed(1)}</div>
          <div className={styles.statLabel}>Current WPM</div>
          {stats.skill_profile.improvement_week !== null && (
            <div className={styles.statTrend}>
              {stats.skill_profile.improvement_week > 0 ? '↑' : '→'} {Math.abs(stats.skill_profile.improvement_week).toFixed(1)}% this week
            </div>
          )}
        </div>

        <div className={styles.statCard}>
          <div className={styles.statIcon}>🎯</div>
          <div className={styles.statValue}>{stats.skill_profile.avg_accuracy.toFixed(1)}%</div>
          <div className={styles.statLabel}>Accuracy</div>
          {stats.skill_profile.best_accuracy && (
            <div className={styles.statTrend}>Best: {stats.skill_profile.best_accuracy.toFixed(1)}%</div>
          )}
        </div>

        <div className={styles.statCard}>
          <div className={styles.statIcon}>📊</div>
          <div className={styles.statValue}>{stats.skill_profile.consistency_score.toFixed(0)}</div>
          <div className={styles.statLabel}>Consistency</div>
          <div className={styles.statTrend}>Very {stats.skill_profile.consistency_score > 85 ? 'stable' : stats.skill_profile.consistency_score > 60 ? 'improving' : 'variable'}</div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statIcon}>🎪</div>
          <div className={styles.statValue}>{stats.skill_profile.total_sessions}</div>
          <div className={styles.statLabel}>Sessions</div>
          <div className={styles.statTrend}>{Math.round(stats.skill_profile.total_sessions * 2)} minutes practice</div>
        </div>
      </div>

      {/* Streaks Section */}
      {stats.streaks.length > 0 && (
        <div className={styles.section}>
          <h2>🔥 Your Streaks</h2>
          <div className={styles.streaksGrid}>
            {stats.streaks.map((streak) => (
              <div key={streak.type} className={styles.streakCard}>
                <div className={styles.streakEmoji}>{getStreakEmoji(streak.type)}</div>
                <div className={styles.streakLabel}>{streak.type === 'days_practiced' ? 'Days Practicing' : 'Error-Free Sessions'}</div>
                <div className={styles.streakCurrent}>{streak.current_count}</div>
                <div className={styles.streakPersonalBest}>Personal best: {streak.longest_count}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className={styles.tabNav}>
        <button
          className={`${styles.tabButton} ${activeTab === 'overview' ? styles.active : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`${styles.tabButton} ${activeTab === 'trends' ? styles.active : ''}`}
          onClick={() => setActiveTab('trends')}
        >
          Trends
        </button>
        <button
          className={`${styles.tabButton} ${activeTab === 'achievements' ? styles.active : ''}`}
          onClick={() => setActiveTab('achievements')}
        >
          Achievements
        </button>
        <button
          className={`${styles.tabButton} ${activeTab === 'heatmap' ? styles.active : ''}`}
          onClick={() => setActiveTab('heatmap')}
        >
          Keyboard Map
        </button>
      </div>

      {/* Tab Content */}
      <div className={styles.tabContent}>
        {activeTab === 'overview' && (
          <div className={styles.section}>
            <h2>Recent Milestones 🎉</h2>
            {stats.recent_milestones.length > 0 ? (
              <div className={styles.milestonesList}>
                {stats.recent_milestones.map((milestone) => (
                  <div key={milestone.type} className={styles.milestoneCard}>
                    <div className={styles.milestoneTitle}>{milestone.title}</div>
                    <div className={styles.milestoneDescription}>{milestone.description}</div>
                    {milestone.metric_value && (
                      <div className={styles.milestoneValue}>{milestone.metric_value.toFixed(1)}</div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className={styles.emptyState}>Keep practicing to reach new milestones!</p>
            )}
          </div>
        )}

        {activeTab === 'trends' && stats.progress_trend.length > 0 && (
          <div className={styles.section}>
            <h2>Your Progress Over Time 📈</h2>
            <div className={styles.chartContainer}>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={stats.progress_trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis yAxisId="left" label={{ value: 'WPM', angle: -90, position: 'insideLeft' }} />
                  <YAxis yAxisId="right" orientation="right" label={{ value: 'Accuracy %', angle: 90, position: 'insideRight' }} />
                  <Tooltip
                    formatter={(value) => (typeof value === 'number' ? value.toFixed(1) : value)}
                    labelFormatter={(label) => new Date(label).toLocaleDateString()}
                  />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="avg_wpm"
                    stroke="#3B82F6"
                    name="WPM"
                    dot={false}
                    strokeWidth={2}
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="avg_accuracy"
                    stroke="#10B981"
                    name="Accuracy %"
                    dot={false}
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {activeTab === 'achievements' && (
          <div className={styles.section}>
            <h2>Achievements 🏆</h2>
            {stats.achievements.length > 0 ? (
              <div className={styles.achievementsGrid}>
                {stats.achievements.map((achievement) => (
                  <div
                    key={achievement.type}
                    className={styles.achievementBadge}
                    style={{ borderColor: getRarityColor(achievement.rarity) }}
                  >
                    <div className={styles.badgeIcon}>{achievement.icon || '🏅'}</div>
                    <div className={styles.badgeTitle}>{achievement.title}</div>
                    <div className={styles.badgeRarity}>{achievement.rarity}</div>
                    <div className={styles.badgeDate}>
                      {new Date(achievement.earned_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className={styles.emptyState}>Start typing to earn achievements!</p>
            )}
          </div>
        )}

        {activeTab === 'heatmap' && heatmap && (
          <div className={styles.section}>
            <h2>Keyboard Heatmap 🔥</h2>
            <div className={styles.heatmapContainer}>
              <div className={styles.heatmapGrid}>
                {Object.entries(heatmap.heatmap)
                  .sort((a, b) => b[1].error_rate - a[1].error_rate)
                  .map(([char, data]) => (
                    <div
                      key={char}
                      className={styles.heatmapKey}
                      style={{
                        backgroundColor: `var(--color-${data.color})`,
                      }}
                      title={`${char}: ${(data.error_rate * 100).toFixed(1)}% error rate`}
                    >
                      <div className={styles.keyChar}>{char}</div>
                      <div className={styles.keyError}>{(data.error_rate * 100).toFixed(0)}%</div>
                    </div>
                  ))}
              </div>
              <div className={styles.heatmapLegend}>
                <div className={styles.legendItem}><span className={styles.legendGreen}></span> Low error rate</div>
                <div className={styles.legendItem}><span className={styles.legendYellow}></span> Moderate errors</div>
                <div className={styles.legendItem}><span className={styles.legendRed}></span> High error rate</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressDashboard;
