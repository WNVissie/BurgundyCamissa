import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { cn } from '../../lib/utils';
import {
  LayoutDashboard,
  Calendar,
  Users,
  BarChart3,
  Settings,
  Shield,
  Clock,
  FileText,
  Plane,
  MessageCircle,
  LifeBuoy,
  X
} from 'lucide-react';
import { Button } from '../ui/button';

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    roles: ['Admin', 'Manager', 'Employee']
  },
  {
    name: 'Shift Roster',
    href: '/roster',
    icon: Calendar,
    roles: ['Admin', 'Manager', 'Employee']
  },
  {
    name: 'Timesheets',
    href: '/timesheets',
    icon: Clock,
    roles: ['Admin', 'Manager', 'Employee']
  },
  {
    name: 'Leave',
    href: '/leave',
    icon: Plane,
    roles: ['Admin', 'Manager', 'Employee']
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
    roles: ['Admin', 'Manager']
  },
  {
    name: 'Employees',
    href: '/employees',
    icon: Users,
    roles: ['Admin', 'Manager']
  },
  {
    name: 'Reports',
    href: '/reports',
    icon: FileText,
    roles: ['Admin', 'Manager']
  },
  {
    name: 'Admin Panel',
    href: '/admin',
    icon: Shield,
    roles: ['Admin']
  },
  {
    name: 'Community',
    href: '/community',
    icon: MessageCircle,
    roles: ['Admin', 'Manager', 'Employee']
  },
  {
    name: 'Support',
    href: 'https://wa.me/1234567890?text=I%20need%20support%20with%20the%20roster%20app.',
    icon: LifeBuoy,
    roles: ['Admin', 'Manager', 'Employee'],
    external: true
  }
];

export function Sidebar({ isOpen, onClose }) {
  const location = useLocation();
  const { user } = useAuth();

  const filteredNavigation = navigation.filter(item => 
    item.roles.includes(user?.role?.name)
  );

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div className={cn(
        "fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 transform transition-transform duration-200 ease-in-out lg:translate-x-0 lg:static lg:inset-0",
        isOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex flex-col h-full">
          {/* Mobile close button */}
          <div className="flex items-center justify-between p-4 lg:hidden">
            <span className="text-lg font-semibold">Menu</span>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {filteredNavigation.map((item) => {
              const isActive = !item.external && location.pathname === item.href;
              const linkClasses = cn(
                "flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                isActive
                  ? "bg-blue-100 text-blue-700"
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              );

              if (item.external) {
                return (
                  <a
                    key={item.name}
                    href={item.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={linkClasses}
                  >
                    <item.icon className="mr-3 h-5 w-5" />
                    {item.name}
                  </a>
                );
              }

              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={onClose}
                  className={linkClasses}
                >
                  <item.icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* User info */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">
                    {user?.name?.charAt(0)}{user?.surname?.charAt(0)}
                  </span>
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">
                  {user?.name} {user?.surname}
                </p>
                <p className="text-xs text-gray-500">
                  {user?.role?.name}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

