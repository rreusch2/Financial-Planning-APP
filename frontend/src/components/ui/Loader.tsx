import React from 'react';
import { cn } from '../../lib/utils';

interface LoaderProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-8 w-8',
  lg: 'h-12 w-12',
};

export function Loader({ size = 'md', className }: LoaderProps) {
  return (
    <div
      className={cn(
        'animate-spin rounded-full border-b-2 border-indigo-600',
        sizeClasses[size],
        className
      )}
    />
  );
}
























