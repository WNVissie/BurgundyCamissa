import React from 'react';

const Badge = ({ count, color = 'red', className = '' }) => {
  if (!count || count === 0) return null;

  const baseClasses = 'inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 rounded-full';
  
  const colorClasses = {
    red: 'bg-red-600',
    orange: 'bg-orange-500',
    blue: 'bg-blue-600',
    green: 'bg-green-600',
  };

  return (
    <span className={`${baseClasses} ${colorClasses[color] || colorClasses.red} ${className}`}>
      {count > 99 ? '99+' : count}
    </span>
  );
};

export default Badge;