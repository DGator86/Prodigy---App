import React from 'react';
import { useLocation, useNavigate, useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, CheckCircle, Activity, Zap, Repeat, PieChart } from 'lucide-react';
import { workoutsApi } from '../api/client';
import { Card, CardHeader, MetricCard, ConfidenceBadge } from '../components/common/Card';
import { Button } from '../components/common/Button';
import {
  formatEWU,
  formatPercent,
  formatTime,
  getWorkoutTypeLabel,
  getMovementLabel,
  getDomainLabel,
} from '../utils/formatters';

export function WorkoutResults() {
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams();
  
  // Get data from navigation state (just created) or fetch it
  const stateData = location.state?.data;
  
  const { data: fetchedData, isLoading } = useQuery({
    queryKey: ['workout', id],
    queryFn: () => workoutsApi.get(id!),
    enabled: !stateData && !!id,
  });
  
  const data = stateData || fetchedData;
  const workout = stateData?.workout || fetchedData;
  const metrics = stateData?.metrics || fetchedData?.metrics;
  const domainsUpdated = stateData?.domains_updated || [];
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-pulse text-gray-400">Loading...</div>
      </div>
    );
  }
  
  if (!data || !workout) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <p className="text-gray-500 mb-4">Workout not found</p>
        <Button onClick={() => navigate('/dashboard')}>Go to Dashboard</Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Success Header */}
      {stateData && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-6 mb-8 flex items-center gap-4">
          <CheckCircle className="w-12 h-12 text-green-500 flex-shrink-0" />
          <div>
            <h1 className="text-xl font-bold text-green-800">Workout Logged!</h1>
            <p className="text-green-700">
              Your metrics have been calculated and domains updated.
            </p>
          </div>
        </div>
      )}

      {/* Back button for non-new view */}
      {!stateData && (
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>
      )}

      {/* Workout Title */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          {workout.name || 'Workout Results'}
        </h1>
        <div className="flex items-center gap-3 mt-2">
          <span className="badge badge-info">
            {getWorkoutTypeLabel(workout.workout_type)}
          </span>
          <span className="text-gray-500">
            {formatTime(workout.total_time_seconds)} total time
          </span>
          {workout.round_count > 1 && (
            <span className="text-gray-500">
              {workout.round_count} rounds
            </span>
          )}
        </div>
      </div>

      {/* Main Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <MetricCard
          label="Total EWU"
          value={formatEWU(metrics?.total_ewu || 0)}
          icon={<Activity className="w-5 h-5" />}
        />
        <MetricCard
          label="Density Power"
          value={metrics?.density_power_min?.toFixed(2) || '0'}
          unit="EWU/min"
          icon={<Zap className="w-5 h-5" />}
        />
        {metrics?.active_power && (
          <MetricCard
            label="Active Power"
            value={metrics.active_power.average_active_power?.toFixed(2) || '0'}
            unit="EWU/min"
            icon={<Zap className="w-5 h-5" />}
          />
        )}
        <MetricCard
          label="Modality"
          value={`${formatPercent(metrics?.lift_share || 0, 0)} Lift`}
          icon={<PieChart className="w-5 h-5" />}
        />
      </div>

      {/* Repeatability */}
      {metrics?.repeatability && (
        <Card className="mb-8">
          <CardHeader
            title="Repeatability Metrics"
            subtitle="How consistent were you across rounds?"
          />
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500">Drift</p>
              <p className="text-2xl font-bold text-gray-900">
                {metrics.repeatability.drift !== null
                  ? formatPercent(metrics.repeatability.drift)
                  : 'N/A'}
              </p>
              <p className="text-xs text-gray-400">
                {(metrics.repeatability.drift || 0) > 0 ? 'Slowing down' : 'Stable/faster'}
              </p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500">Spread</p>
              <p className="text-2xl font-bold text-gray-900">
                {metrics.repeatability.spread !== null
                  ? formatPercent(metrics.repeatability.spread)
                  : 'N/A'}
              </p>
              <p className="text-xs text-gray-400">Best vs worst variance</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500">Consistency</p>
              <p className="text-2xl font-bold text-gray-900">
                {metrics.repeatability.consistency !== null
                  ? formatPercent(metrics.repeatability.consistency)
                  : 'N/A'}
              </p>
              <p className="text-xs text-gray-400">Higher is better</p>
            </div>
          </div>
          
          {/* Split times */}
          {workout.splits?.length > 0 && (
            <div className="mt-4 pt-4 border-t">
              <p className="text-sm text-gray-500 mb-2">Split Times</p>
              <div className="flex flex-wrap gap-2">
                {workout.splits.map((split: any) => (
                  <span
                    key={split.round_number}
                    className="px-3 py-1 bg-gray-100 rounded-full text-sm"
                  >
                    R{split.round_number}: {formatTime(split.time_seconds)}
                  </span>
                ))}
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Modality Breakdown */}
      <Card className="mb-8">
        <CardHeader title="Modality Breakdown" />
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">Lift</span>
              <span className="font-medium">
                {formatEWU(metrics?.lift_ewu || 0)} EWU ({formatPercent(metrics?.lift_share || 0)})
              </span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-red-500 rounded-full"
                style={{ width: `${(metrics?.lift_share || 0) * 100}%` }}
              />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">Machine</span>
              <span className="font-medium">
                {formatEWU(metrics?.machine_ewu || 0)} EWU ({formatPercent(metrics?.machine_share || 0)})
              </span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 rounded-full"
                style={{ width: `${(metrics?.machine_share || 0) * 100}%` }}
              />
            </div>
          </div>
          {(metrics?.gymnastics_share || 0) > 0 && (
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Gymnastics</span>
                <span className="font-medium">
                  {formatEWU(metrics?.gymnastics_ewu || 0)} EWU ({formatPercent(metrics?.gymnastics_share || 0)})
                </span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-purple-500 rounded-full"
                  style={{ width: `${(metrics?.gymnastics_share || 0) * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Movements */}
      <Card className="mb-8">
        <CardHeader title="Movements" />
        <div className="space-y-2">
          {workout.movements?.map((movement: any, index: number) => (
            <div
              key={movement.id || index}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div>
                <span className="font-medium">
                  {getMovementLabel(movement.movement_type)}
                </span>
                <span className="text-gray-500 ml-2">
                  {movement.modality === 'machine'
                    ? `${movement.calories} cal`
                    : movement.load_lb
                    ? `${movement.reps} @ ${movement.load_lb} lb`
                    : `${movement.reps} reps`}
                </span>
              </div>
              <span className="text-sm text-gray-400 capitalize">
                {movement.modality}
              </span>
            </div>
          ))}
        </div>
      </Card>

      {/* Domains Updated */}
      {domainsUpdated.length > 0 && (
        <Card className="mb-8">
          <CardHeader
            title="Domains Updated"
            subtitle="This workout contributed to these performance domains"
          />
          <div className="flex flex-wrap gap-2">
            {domainsUpdated.map((domain: string) => (
              <Link
                key={domain}
                to={`/domain/${domain}`}
                className="badge badge-success hover:bg-green-200 transition-colors"
              >
                {getDomainLabel(domain)}
              </Link>
            ))}
          </div>
        </Card>
      )}

      {/* Notes */}
      {workout.notes && (
        <Card className="mb-8">
          <CardHeader title="Notes" />
          <p className="text-gray-700 whitespace-pre-wrap">{workout.notes}</p>
        </Card>
      )}

      {/* Actions */}
      <div className="flex gap-4">
        <Button
          variant="secondary"
          onClick={() => navigate('/dashboard')}
          className="flex-1"
        >
          Go to Dashboard
        </Button>
        <Button
          onClick={() => navigate('/log')}
          className="flex-1"
        >
          Log Another Workout
        </Button>
      </div>
    </div>
  );
}
