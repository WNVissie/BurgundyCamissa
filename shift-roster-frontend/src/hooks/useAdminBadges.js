import { useState, useEffect, useCallback } from 'react';
import { timesheetsAPI, rosterAPI, leaveAPI, notificationsAPI } from '../lib/api';

// Custom hook for admin badge notifications
export const useAdminBadges = (isAdmin = false) => {
  const [badges, setBadges] = useState({
    timesheets: 0,
    roster: 0,
    leave: 0,
    notifications: 0,
  });
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);

  const fetchPendingCounts = useCallback(async () => {
    if (!isAdmin) return;

    try {
      setLoading(true);
      const [timesheetsRes, rosterRes, leaveRes, notificationsRes] = await Promise.allSettled([
        timesheetsAPI.getPendingCount(),
        rosterAPI.getPendingCount(),
        leaveAPI.getPendingCount(),
        notificationsAPI.getUnread(),
      ]);

      setBadges({
        timesheets: timesheetsRes.status === 'fulfilled' ? timesheetsRes.value.data.pending_count : 0,
        roster: rosterRes.status === 'fulfilled' ? rosterRes.value.data.pending_count : 0,
        leave: leaveRes.status === 'fulfilled' ? leaveRes.value.data.pending_count : 0,
        notifications: notificationsRes.status === 'fulfilled' ? notificationsRes.value.data.length : 0,
      });

      if (notificationsRes.status === 'fulfilled') {
        setNotifications(notificationsRes.value.data);
      }
    } catch (error) {
      console.error('Error fetching pending counts:', error);
    } finally {
      setLoading(false);
    }
  }, [isAdmin]);

  const markNotificationAsRead = async (notificationId) => {
    try {
      await notificationsAPI.markAsRead(notificationId);
      // Remove from local state
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
      setBadges(prev => ({ ...prev, notifications: Math.max(0, prev.notifications - 1) }));
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  // Poll for updates every 30 seconds
  useEffect(() => {
    if (isAdmin) {
      fetchPendingCounts();
      const interval = setInterval(fetchPendingCounts, 30000);
      return () => clearInterval(interval);
    }
  }, [isAdmin, fetchPendingCounts]);

  return {
    badges,
    notifications,
    loading,
    refetch: fetchPendingCounts,
    markNotificationAsRead,
  };
};