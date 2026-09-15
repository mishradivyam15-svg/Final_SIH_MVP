import type { ButtonHTMLAttributes, ReactNode } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md';
}

const VARIANT_CLASSES: Record<NonNullable<ButtonProps['variant']>, string> = {
  primary:
    'bg-brand-700 text-white shadow-sm hover:bg-brand-800 hover:shadow-glow focus-visible:ring-brand-700',
  secondary:
    'bg-surface text-ink-700 border border-ink-300 hover:border-brand-300 hover:bg-surface-subtle focus-visible:ring-brand-700',
  danger:
    'bg-surface text-priority-high border border-priority-highBorder hover:bg-priority-highBg focus-visible:ring-priority-high',
  ghost: 'bg-transparent text-ink-700 hover:bg-surface-muted focus-visible:ring-brand-700',
};

const SIZE_CLASSES: Record<NonNullable<ButtonProps['size']>, string> = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
};

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  disabled,
  ...rest
}: ButtonProps) {
  return (
    <button
      className={`inline-flex transform-gpu items-center justify-center gap-2 rounded-md font-medium transition-all duration-200 ease-out hover:scale-105 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 active:scale-[0.97] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:scale-100 disabled:active:scale-100 ${VARIANT_CLASSES[variant]} ${SIZE_CLASSES[size]} ${className}`}
      disabled={disabled}
      {...rest}
    >
      {children}
    </button>
  );
}
