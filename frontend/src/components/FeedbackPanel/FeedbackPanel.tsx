/**
 * Feedback Panel Component
 *
 * Displays motivational messages, achievement celebrations, and milestone announcements.
 * The reassuring voice that says "you're doing great."
 */

import React, { useEffect, useState } from 'react';
import styles from './FeedbackPanel.module.css';

interface FeedbackMessage {
  id: string;
  type: 'achievement' | 'milestone' | 'encouragement' | 'improvement' | 'streak';
  title: string;
  message: string;
  emoji?: string;
  duration?: number; // milliseconds
  action?: () => void;
}

interface FeedbackPanelProps {
  userId: number;
  onMessageDismiss?: (id: string) => void;
}

export const FeedbackPanel: React.FC<FeedbackPanelProps> = ({ userId, onMessageDismiss }) => {
  const [messages, setMessages] = useState<FeedbackMessage[]>([]);

  useEffect(() => {
    // Subscribe to feedback messages from exercise completion
    const handleExerciseComplete = async (event: CustomEvent) => {
      const progressResult = event.detail;

      const newMessages: FeedbackMessage[] = [];

      // Achievement messages
      if (progressResult.new_achievements && progressResult.new_achievements.length > 0) {
        progressResult.new_achievements.forEach((achievement: any) => {
          newMessages.push({
            id: `achievement-${achievement.type}`,
            type: 'achievement',
            title: achievement.title,
            message: achievement.message,
            emoji: '🏆',
            duration: 5000,
          });
        });
      }

      // Milestone messages
      if (progressResult.new_milestones && progressResult.new_milestones.length > 0) {
        progressResult.new_milestones.forEach((milestone: any) => {
          newMessages.push({
            id: `milestone-${milestone.type}`,
            type: 'milestone',
            title: milestone.title,
            message: milestone.message,
            emoji: '🎉',
            duration: 6000,
          });
        });
      }

      // Streak updates
      if (progressResult.streak_updates) {
        const streaks = progressResult.streak_updates;
        if (streaks.daily_streak && streaks.daily_streak.current >= 3) {
          newMessages.push({
            id: `streak-daily`,
            type: 'streak',
            title: '🔥 On Fire!',
            message: `${streaks.daily_streak.current}-day streak! Keep going!`,
            emoji: '🔥',
            duration: 4000,
          });
        }
        if (streaks.error_free_streak && streaks.error_free_streak.current >= 2) {
          newMessages.push({
            id: `streak-error-free`,
            type: 'streak',
            title: '⭐ Perfect Sessions',
            message: `${streaks.error_free_streak.current} perfect sessions in a row!`,
            emoji: '⭐',
            duration: 4000,
          });
        }
      }

      // Motivational message
      if (progressResult.motivational_message) {
        newMessages.push({
          id: `motivation-${Date.now()}`,
          type: 'encouragement',
          title: 'Great Job!',
          message: progressResult.motivational_message,
          emoji: '💪',
          duration: 4000,
        });
      }

      setMessages((prev) => [...prev, ...newMessages]);
    };

    window.addEventListener('exercise-complete', handleExerciseComplete as EventListener);
    return () => window.removeEventListener('exercise-complete', handleExerciseComplete as EventListener);
  }, []);

  useEffect(() => {
    // Auto-dismiss messages after their duration
    const timers: NodeJS.Timeout[] = [];

    messages.forEach((message) => {
      if (message.duration) {
        const timer = setTimeout(() => {
          dismissMessage(message.id);
        }, message.duration);
        timers.push(timer);
      }
    });

    return () => {
      timers.forEach((timer) => clearTimeout(timer));
    };
  }, [messages]);

  const dismissMessage = (id: string) => {
    setMessages((prev) => prev.filter((msg) => msg.id !== id));
    onMessageDismiss?.(id);
  };

  if (messages.length === 0) {
    return null;
  }

  return (
    <div className={styles.feedbackContainer}>
      {messages.map((message) => (
        <div key={message.id} className={`${styles.feedbackMessage} ${styles[message.type]}`}>
          <div className={styles.feedbackContent}>
            <div className={styles.emoji}>{message.emoji}</div>
            <div className={styles.textContent}>
              <div className={styles.title}>{message.title}</div>
              <div className={styles.message}>{message.message}</div>
            </div>
          </div>
          <button
            className={styles.dismissButton}
            onClick={() => dismissMessage(message.id)}
            aria-label="Dismiss"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
};

export default FeedbackPanel;
