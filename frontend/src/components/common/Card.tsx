import React from 'react';
import { clsx } from 'clsx';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export function Card({ children, className, padding = 'md' }: CardProps) {
  const paddingStyles = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div
      className={clsx(
        'bg-white rounded-xl shadow-sm border border-gray-100',
        paddingStyles[padding],
        className
      )}
    >
      {children}
    </div>
  );
}

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export function CardHeader({ title, subtitle, action }: CardHeaderProps) {
  return (
    <div className="flex items-start justify-between mb-4">
      <div>
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  change?: number;
  changeLabel?: string;
  icon?: React.ReactNode;
  className?: string;
}

export function MetricCard({
  label,
  value,
  unit,
  change,
  changeLabel,
  icon,
  className,
}: MetricCardProps) {
  const isPositiveChange = change && change > 0;
  const isNegativeChange = change && change < 0;

  return (
    <Card className={clsx('relative overflow-hidden', className)}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {value}
            {unit && <span className="text-lg font-normal text-gray-500 ml-1">{unit}</span>}
          </p>
          {change !== undefined && (
            <p
              className={clsx(
                'text-sm mt-1',
                isPositiveChange && 'text-green-600',
                isNegativeChange && 'text-red-600',
                !isPositiveChange && !isNegativeChange && 'text-gray-500'
              )}
            >
              {isPositiveChange && '+'}
              {change.toFixed(1)}%
              {changeLabel && <span className="text-gray-400 ml-1">{changeLabel}</span>}
            </p>
          )}
        </div>
        {icon && (
          <div className="p-2 bg-primary-100 rounded-lg text-primary-600">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}

interface ConfidenceBadgeProps {
  confidence: string;
  sampleCount?: number;
}

export function ConfidenceBadge({ confidence, sampleCount }: ConfidenceBadgeProps) {
  const styles: Record<string, string> = {
    high: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-red-100 text-red-800',
    no_data: 'bg-gray-100 text-gray-600',
  };

  const labels: Record<string, string> = {
    high: 'High Confidence',
    medium: 'Medium Confidence',
    low: 'Low Confidence',
    no_data: 'No Data',
  };

  return (
    <span className={clsx('badge', styles[confidence] || styles.no_data)}>
      {labels[confidence] || confidence}
      {sampleCount !== undefined && confidence !== 'no_data' && (
        <span className="ml-1 opacity-70">({sampleCount})</span>
      )}
    </span>
  );
}
