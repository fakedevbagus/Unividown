'use client';

import React, { ButtonHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

export function Button({
  variant = 'primary',
  size = 'md',
  className,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed select-none',
        variant === 'primary' &&
          'bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white shadow-sm dark:bg-indigo-500 dark:hover:bg-indigo-600',
        variant === 'secondary' &&
          'bg-purple-600 hover:bg-purple-700 active:bg-purple-800 text-white shadow-sm dark:bg-purple-500 dark:hover:bg-purple-600',
        variant === 'outline' &&
          'border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800',
        variant === 'ghost' &&
          'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800',
        variant === 'danger' &&
          'bg-red-500 hover:bg-red-600 text-white shadow-sm',
        size === 'sm' && 'px-3 py-1.5 text-xs gap-1.5',
        size === 'md' && 'px-4 py-2 text-sm gap-2',
        size === 'lg' && 'px-6 py-3 text-base gap-2.5',
        'hover:scale-[1.02] active:scale-[0.98]',
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
