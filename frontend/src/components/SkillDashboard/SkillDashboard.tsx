/**
 * User Skill Dashboard Component
 * 
 * Displays personalized skill profile with:
 * - Overview metrics (WPM, accuracy)
 * - Performance trends
 * - Weak key identification
 * - Coaching insights
 * - Achievement streaks
 * 
 * Makes users feel "known" and understood through their data
 */

import React, { useEffect, useState } from 'react';
import styles from './SkillDashboard.module.css';

interface SkillProfile {
  user_id: number;
  avg_wpm: number;
  avg_accuracy: number;
  total_sessions: number;
  total_keystrokes: number;
  improvement_week: number | null;
  consistency_score: number;
  weak_keys: Record<string, { frequency: number; error_rate: number }>;
  best_wpm: number | null;
  best_accuracy: number | null;
  current_streak: number;
}

interface Insight {
  insight_type: string;
  title: string;
  description: string;
  tone: string;
  priority: number;
}

interface SkillDashboardProps {
  userId: number;
  sessionId?: number;
}

export const SkillDashboard: React.FC<SkillDashboardProps> = ({ userId, sessionId }) => {
  const [profile, setProfile] = useState<SkillProfile | null>(null);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        setError(null);

        // Trigger profile update if session ID provided
        if (sessionId) {
          const updateResponse = await fetch(
            `/api/v1/users/${userId}/profile/update-session?session_id=${sessionId}`,
            { method: 'POST' }
          );

          if (!updateResponse.ok) {
            console.warn('Profile update request failed');
          }
        }

        // Fetch profile
        const profileResponse = await fetch(
          `/api/v1/users/${userId}/skill-profile`
        );

        if (!profileResponse.ok) {
          if (profileResponse.status === 404) {
            setError(
              'Profile not ready yet. Complete a few more sessions to see your skill profile.'
            );
          } else {
            throw new Error('Failed to fetch profile');
          }
          setLoading(false);
          return;
        }

        const profileData = await profileResponse.json();
        setProfile(profileData);

        // Fetch insights
        const insightsResponse = await fetch(
          `/api/v1/users/${userId}/insights?limit=5`
        );

        if (insightsResponse.ok) {
          const insightsData = await insightsResponse.json();
          setInsights(insightsData);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Error fetching profile:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [userId, sessionId]);

  if (loading) {
    return (
      <div className={styles.dashboardContainer}>
        <div className={styles.loadingState}>
          <div className={styles.spinner} />
          <p>Loading your skill profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.dashboardContainer}>
        <div className={styles.errorState}>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!profile) {
    return null;
  }

  const weakKeysArray = Object.entries(profile.weak_keys).map(([char, stats]) => ({
    char,
    ...stats,
  }));

  const getStreakEmoji = (streak: number): string => {
    if (streak === 0) return '';
    if (streak < 3) return '🔥';
    if (streak < 7) return '🔥🔥';
    return '🔥🔥🔥';
  };

  const getTrendArrow = (improvement: number | null): string => {
    if (!improvement) return '→';
    if (improvement > 5) return '↗️ +' + improvement.toFixed(1) + '%';
    if (improvement < -5) return '↘️ ' + improvement.toFixed(1) + '%';
    return '→';
  };

  return (
    <div className={styles.dashboardContainer}>
      {/* Header */}
      <div className={styles.header}>
        <h1>Your Typing Profile</h1>
        <p>Data that knows you</p>
      </div>

      {/* Core Metrics */}
      <div className={styles.metricsGrid}>
        <div className={styles.metricCard}>
          <div className={styles.metricIcon}>⚡</div>
          <div className={styles.metricValue}>{profile.avg_wpm.toFixed(1)}</div>
          <div className={styles.metricLabel}>WPM</div>
          <div className={styles.metricTrend}>
            {getTrendArrow(profile.improvement_week)}
          </div>
          <div className={styles.metricSubtitle}>
            Best: {profile.best_wpm?.toFixed(0) || '—'}
          </div>
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricIcon}>🎯</div>
          <div className={styles.metricValue}>{profile.avg_accuracy.toFixed(1)}%</div>
          <div className={styles.metricLabel}>Accuracy</div>
          <div className={styles.metricTrend}>
            {profile.avg_accuracy >= 95 ? '✓ Excellent' : 'Room to grow'}
          </div>
          <div className={styles.metricSubtitle}>
            Best: {profile.best_accuracy?.toFixed(1)}%
          </div>
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricIcon}>📊</div>
          <div className={styles.metricValue}>{profile.total_sessions}</div>
          <div className={styles.metricLabel}>Sessions</div>
          <div className={styles.metricTrend}>Consistency: {profile.consistency_score.toFixed(0)}%</div>
          <div className={styles.metricSubtitle}>
            {profile.total_keystrokes.toLocaleString()} keystrokes
          </div>
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricIcon}>{getStreakEmoji(profile.current_streak)}</div>
          <div className={styles.metricValue}>{profile.current_streak}</div>
          <div className={styles.metricLabel}>Perfect Streak</div>
          <div className={styles.metricTrend}>
            {profile.current_streak > 0
              ? `${profile.current_streak} sessions error-free!`
              : 'Build your streak'}
          </div>
        </div>
      </div>

      {/* Insights Section */}
      {insights.length > 0 && (
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>💡 What We Notice</h2>
          <div className={styles.insightsList}>
            {insights.map((insight, index) => (
              <div key={index} className={`${styles.insightCard} ${styles[insight.tone]}`}>
                <div className={styles.insightIcon}>
                  {insight.insight_type === 'strength' && '⭐'}
                  {insight.insight_type === 'weakness' && '🎯'}
                  {insight.insight_type === 'improvement' && '📈'}
                  {insight.insight_type === 'pattern' && '🔍'}
                  {insight.insight_type === 'milestone' && '🏆'}
                </div>
                <div className={styles.insightContent}>
                  <h3 className={styles.insightTitle}>{insight.title}</h3>
                  <p className={styles.insightDescription}>{insight.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Weak Keys */}
      {weakKeysArray.length > 0 && (
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>🔴 Keys That Need Love</h2>
          <div className={styles.weakKeysList}>
            {weakKeysArray.slice(0, 5).map((key) => (
              <div key={key.char} className={styles.weakKeyItem}>
                <div className={styles.keyChar}>{key.char === ' ' ? '⎵' : key.char}</div>
                <div className={styles.keyStats}>
                  <div className={styles.keyAttempts}>
                    {key.frequency} attempts
                  </div>
                  <div className={styles.keyErrorRate}>
                    {(key.error_rate * 100).toFixed(0)}% error rate
                  </div>
                </div>
                <div className={styles.keyBar}>
                  <div
                    className={styles.keyBarFill}
                    style={{ width: `${key.error_rate * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Status Message */}
      <div className={styles.statusMessage}>
        <p>
          {profile.avg_accuracy >= 98
            ? "You're typing like a pro. Keep pushing your speed."
            : profile.avg_accuracy >= 95
            ? 'Great accuracy. Time to build speed.'
            : "Don't worry about speed yet—let's nail accuracy first."}
        </p>
      </div>
    </div>
  );
};

export default SkillDashboard;
