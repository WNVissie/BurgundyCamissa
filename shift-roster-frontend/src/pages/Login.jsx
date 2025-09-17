import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Calendar, AlertCircle } from 'lucide-react';
import '../App.css';

export function Login() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login, error } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulate Google OAuth login with development credentials
    const mockCredentials = {
      email: email,
      google_id: `dev_${email.replace('@', '_').replace('.', '_')}`,
      name: email.split('@')[0].split('.')[0] || 'User',
      surname: email.split('@')[0].split('.')[1] || 'Test'
    };

    const result = await login(mockCredentials);
    
    if (result.success) {
      navigate(from, { replace: true });
    }
    
    setIsLoading(false);
  };

  const handleDemoLogin = async (userType) => {
    setIsLoading(true);
    
    const demoUsers = {
      admin: {
        email: 'admin@company.com',
        google_id: 'admin123',
        name: 'John',
        surname: 'Admin'
      },
      manager: {
        email: 'manager@company.com',
        google_id: 'manager123',
        name: 'Jane',
        surname: 'Manager'
      },
      employee: {
        email: 'employee1@company.com',
        google_id: 'employee123',
        name: 'Bob',
        surname: 'Employee'
      }
    };

    const result = await login(demoUsers[userType]);
    
    if (result.success) {
      navigate(from, { replace: true });
    }
    
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="flex justify-center">
            <Calendar className="h-12 w-12 text-blue-600" />
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Employee Shift Roster
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Sign in to manage your shifts and schedules
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Sign In</CardTitle>
            <CardDescription>
              Enter your email to sign in with Google OAuth (Development Mode)
            </CardDescription>
          </CardHeader>
          <CardContent>
            {error && (
              <Alert variant="destructive" className="mb-4">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="email">Email address</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  required
                  className="mt-1"
                />
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={isLoading || !email}
              >
                {isLoading ? 'Signing in...' : 'Sign in with Google'}
              </Button>
            </form>

            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">Or try demo accounts</span>
                </div>
              </div>

              <div className="mt-6 grid grid-cols-1 gap-3">
                <Button
                  variant="outline"
                  onClick={() => handleDemoLogin('admin')}
                  disabled={isLoading}
                  className="w-full"
                >
                  Demo Admin Login
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handleDemoLogin('manager')}
                  disabled={isLoading}
                  className="w-full"
                >
                  Demo Manager Login
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handleDemoLogin('employee')}
                  disabled={isLoading}
                  className="w-full"
                >
                  Demo Employee Login
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="text-center text-sm text-gray-600">
          <p>Development Mode: Google OAuth simulation enabled</p>
          <p className="mt-1">In production, this would use real Google OAuth</p>
        </div>
      </div>
    </div>
  );
}

