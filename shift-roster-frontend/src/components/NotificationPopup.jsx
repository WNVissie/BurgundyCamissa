import React, { useState, useEffect } from 'react';
import { X, Bell, MessageSquare } from 'lucide-react';

const NotificationPopup = ({ notifications, onMarkAsRead, onClose }) => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (notifications.length > 0) {
      setVisible(true);
      // Auto-hide after 5 seconds if not interacted with
      const timer = setTimeout(() => {
        setVisible(false);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [notifications]);

  if (!visible || notifications.length === 0) return null;

  const handleClose = () => {
    setVisible(false);
    if (onClose) onClose();
  };

  const handleMarkAsRead = (notificationId) => {
    onMarkAsRead(notificationId);
  };

  return (
    <div className="fixed top-4 right-4 z-50 max-w-sm">
      <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-4 animate-slide-in-right">
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center">
            <Bell className="w-5 h-5 text-blue-500 mr-2" />
            <h3 className="text-sm font-medium text-gray-900">New Notifications</h3>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        
        <div className="space-y-2 max-h-60 overflow-y-auto">
          {notifications.slice(0, 3).map((notification) => (
            <div
              key={notification.id}
              className="flex items-start p-2 bg-gray-50 rounded-md hover:bg-gray-100 cursor-pointer"
              onClick={() => handleMarkAsRead(notification.id)}
            >
              <MessageSquare className="w-4 h-4 text-blue-500 mt-0.5 mr-2 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-800 truncate">
                  {notification.message}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(notification.created_at).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          
          {notifications.length > 3 && (
            <p className="text-xs text-gray-500 text-center py-2">
              +{notifications.length - 3} more notifications
            </p>
          )}
        </div>
        
        <div className="mt-3 text-center">
          <button
            onClick={handleClose}
            className="text-xs text-blue-600 hover:text-blue-800"
          >
            Dismiss all
          </button>
        </div>
      </div>
    </div>
  );
};

export default NotificationPopup;