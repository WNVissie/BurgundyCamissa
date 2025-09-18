import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { analyticsAPI } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { 
  Users, 
  Calendar, 
  Clock, 
  TrendingUp,
  AlertCircle,
  CheckCircle,
  UserCheck,
  UserX,
  XCircle, // <-- Add this here
  Plus      // <-- Also add Plus if you use it in Icon
} from 'lucide-react';
import '../App.css';

export function Dashboard() {
  const { user, isAdmin, isManager } = useAuth();
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      if (isAdmin() || isManager()) {
        const response = await analyticsAPI.getDashboard();
        setMetrics(response.data.metrics);
        setRecentActivity(response.data.recent_activity || []);
      }
    } catch (err) {
      console.error('Dashboard fetch error:', err); // Debug log
      setError(err.response?.data?.error || 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  }, [isAdmin, isManager]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  // Note: add status color helper here if needed in the future

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {getGreeting()}, {user?.name}!
            </h1>
            <p className="text-gray-600 mt-1">
              Welcome to your shift roster dashboard
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Role</p>
            <Badge variant="secondary" className="mt-1">
              {user?.role?.name}
            </Badge>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <Calendar className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-gray-900">View Schedule</p>
                <p className="text-xs text-gray-500">Check your shifts</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <Clock className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm font-medium text-gray-900">Timesheets</p>
                <p className="text-xs text-gray-500">Track your hours</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {(isAdmin() || isManager()) && (
          <Card className="cursor-pointer" onClick={() => navigate('/analytics')}>
            <CardContent className="p-4">
              <div className="flex items-center space-x-3">
                <TrendingUp className="h-8 w-8 text-purple-600" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Analytics</p>
                  <p className="text-xs text-gray-500">View reports</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Metrics for Admin/Manager */}
      {(isAdmin() || isManager()) && metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Employees</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.total_employees}</div>
              <p className="text-xs text-muted-foreground">
                Active employees in system
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">On Shift Today</CardTitle>
              <UserCheck className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{metrics.employees_on_shift}</div>
              <p className="text-xs text-muted-foreground">
                Currently working
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">On Leave Today</CardTitle>
              <UserX className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">{metrics.employees_on_leave}</div>
              <p className="text-xs text-muted-foreground">
                Currently on leave
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Available</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{metrics.available_employees}</div>
              <p className="text-xs text-muted-foreground">
                Ready for assignment
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Recent Activity */}
      {(isAdmin() || isManager()) && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Latest updates across the system
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.length > 0 ? (
                recentActivity.map((activity) => {
                  const Icon = ({ action }) => {
                    if (action.includes('approve')) return <CheckCircle className="h-5 w-5 text-green-600" />;
                    if (action.includes('reject')) return <XCircle className="h-5 w-5 text-red-600" />;
                    if (action.includes('create')) return <Plus className="h-5 w-5 text-blue-600" />;
                    return <Calendar className="h-5 w-5 text-gray-500" />;
                  };
                  return (
                    <div key={activity.id} className="flex items-center space-x-3">
                      <Icon action={activity.action} />
                      <div className="flex-1">
                        <p className="text-sm font-medium">{activity.details}</p>
                        <p className="text-xs text-gray-500">{activity.user}</p>
                      </div>
                      <span className="text-xs text-gray-500">
                        {new Date(activity.timestamp).toLocaleString()}
                      </span>
                    </div>
                  );
                })
              ) : (
                <p className="text-sm text-gray-500">No recent activities to display.</p>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Links */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Links</CardTitle>
          <CardDescription>
            Frequently used features
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2" onClick={() => navigate('/roster')}>
              <Calendar className="h-6 w-6" />
              <span className="text-sm">My Schedule</span>
            </Button>
            
      <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2" onClick={() => navigate('/timesheets')}>
              <Clock className="h-6 w-6" />
              <span className="text-sm">Timesheets</span>
            </Button>

            {(isAdmin() || isManager()) && (
              <>
        <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2" onClick={() => navigate('/employees')}>
                  <Users className="h-6 w-6" />
                  <span className="text-sm">Employees</span>
                </Button>
                
        <Button variant="outline" className="h-auto p-4 flex flex-col items-center space-y-2" onClick={() => navigate('/analytics')}>
                  <TrendingUp className="h-6 w-6" />
                  <span className="text-sm">Reports</span>
                </Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {error && (
        <Card className="border-red-200">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2 text-red-600">
              <AlertCircle className="h-5 w-5" />
              <span className="text-sm">{error}</span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

