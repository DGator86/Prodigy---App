import React from 'react';
import { clsx } from 'clsx';
import { ConfidenceBadge } from '../common/Card';
import { getDomainLabel } from '../../utils/formatters';

interface DomainCardProps {
  domain: string;
  score: number | null;
  confidence: string;
  sampleCount: number;
  onClick?: () => void;
}

export function DomainCard({
  domain,
  score,
  confidence,
  sampleCount,
  onClick,
}: DomainCardProps) {
  const hasData = score !== null && confidence !== 'no_data';

  // Get color based on score
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Get progress bar color
  const getProgressColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-blue-500';
    if (score >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div
      className={clsx(
        'bg-white rounded-lg border border-gray-100 p-4',
        onClick && 'cursor-pointer hover:border-primary-300 transition-colors'
      )}
      onClick={onClick}
    >
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-medium text-gray-900">{getDomainLabel(domain)}</h4>
        <ConfidenceBadge confidence={confidence} sampleCount={sampleCount} />
      </div>

      {hasData ? (
        <>
          <div className="flex items-baseline gap-1 mb-2">
            <span className={clsx('text-3xl font-bold', getScoreColor(score!))}>
              {score!.toFixed(0)}
            </span>
            <span className="text-gray-400 text-sm">/100</span>
          </div>
          
          {/* Progress bar */}
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={clsx('h-full rounded-full transition-all duration-500', getProgressColor(score!))}
              style={{ width: `${score}%` }}
            />
          </div>
        </>
      ) : (
        <div className="py-4 text-center">
          <p className="text-gray-400 text-sm">No data yet</p>
          <p className="text-gray-400 text-xs mt-1">
            Log {domain.includes('sprint') ? 'sprint workouts' : 'workouts'} to build this score
          </p>
        </div>
      )}
    </div>
  );
}

interface DomainGridProps {
  domains: Array<{
    domain: string;
    normalized_score: number | null;
    confidence: string;
    sample_count: number;
  }>;
  onDomainClick?: (domain: string) => void;
}

export function DomainGrid({ domains, onDomainClick }: DomainGridProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      {domains.map((d) => (
        <DomainCard
          key={d.domain}
          domain={d.domain}
          score={d.normalized_score}
          confidence={d.confidence}
          sampleCount={d.sample_count}
          onClick={onDomainClick ? () => onDomainClick(d.domain) : undefined}
        />
      ))}
    </div>
  );
}
