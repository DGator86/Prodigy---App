import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Calendar, Filter, ChevronLeft, ChevronRight } from 'lucide-react';
import { workoutsApi } from '../api/client';
import { Card, CardHeader } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Select } from '../components/common/Input';
import {
  formatDate,
  formatEWU,
  formatTime,
  getWorkoutTypeLabel,
} from '../utils/formatters';

const WORKOUT_TYPE_OPTIONS = [
  { value: '', label: 'All Types' },
  { value: 'sprint', label: 'Sprint' },
  { value: 'threshold', label: 'Threshold' },
  { value: 'endurance', label: 'Endurance' },
  { value: 'interval', label: 'Interval' },
  { value: 'chipper', label: 'Chipper' },
  { value: 'strength', label: 'Strength' },
  { value: 'monostructural', label: 'Monostructural' },
];

export function History() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  
  const page = parseInt(searchParams.get('page') || '1');
  const workoutType = searchParams.get('type') || '';
  const limit = 10;

  const { data, isLoading, isError } = useQuery({
    queryKey: ['workouts', page, workoutType],
    queryFn: () =>
      workoutsApi.list({
        page,
        limit,
        workout_type: workoutType || undefined,
      }),
  });

  const workouts = data?.workouts || [];
  const pagination = data?.pagination || { page: 1, pages: 1, total: 0 };

  const handlePageChange = (newPage: number) => {
    setSearchParams((prev) => {
      prev.set('page', newPage.toString());
      return prev;
    });
  };

  const handleTypeFilter = (type: string) => {
    setSearchParams((prev) => {
      if (type) {
        prev.set('type', type);
      } else {
        prev.delete('type');
      }
      prev.set('page', '1');
      return prev;
    });
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Workout History</h1>
          <p className="text-gray-500">
            {pagination.total} workout{pagination.total !== 1 ? 's' : ''} logged
          </p>
        </div>
        <Button onClick={() => navigate('/log')}>Log Workout</Button>
      </div>

      {/* Filters */}
      <Card className="mb-6" padding="sm">
        <div className="flex items-center gap-4">
          <Filter className="w-4 h-4 text-gray-400" />
          <Select
            options={WORKOUT_TYPE_OPTIONS}
            value={workoutType}
            onChange={(e) => handleTypeFilter(e.target.value)}
            className="w-48"
          />
        </div>
      </Card>

      {/* Workout List */}
      {isLoading ? (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="animate-pulse bg-gray-100 h-24 rounded-xl" />
          ))}
        </div>
      ) : isError ? (
        <Card className="text-center py-12">
          <p className="text-red-500 mb-4">Failed to load workouts</p>
          <Button variant="outline" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </Card>
      ) : workouts.length === 0 ? (
        <Card className="text-center py-12">
          <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 mb-4">
            {workoutType ? 'No workouts match this filter' : 'No workouts logged yet'}
          </p>
          <Button onClick={() => navigate('/log')}>Log Your First Workout</Button>
        </Card>
      ) : (
        <div className="space-y-4">
          {workouts.map((workout: any) => (
            <Link
              key={workout.id}
              to={`/workout/${workout.id}`}
              className="block"
            >
              <Card
                className="hover:border-primary-300 hover:shadow-md transition-all"
                padding="sm"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="font-semibold text-gray-900">
                        {workout.name || 'Workout'}
                      </h3>
                      <span className="badge badge-info text-xs">
                        {getWorkoutTypeLabel(workout.workout_type)}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>{formatDate(workout.performed_at)}</span>
                      <span>{formatTime(workout.total_time_seconds)}</span>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <p className="text-xl font-bold text-primary-600">
                      {formatEWU(workout.total_ewu || 0)}
                      <span className="text-sm font-normal text-gray-400 ml-1">
                        EWU
                      </span>
                    </p>
                    {workout.density_power_min && (
                      <p className="text-sm text-gray-500">
                        {workout.density_power_min.toFixed(2)} EWU/min
                      </p>
                    )}
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {/* Pagination */}
      {pagination.pages > 1 && (
        <div className="flex items-center justify-center gap-4 mt-8">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handlePageChange(page - 1)}
            disabled={page <= 1}
          >
            <ChevronLeft className="w-4 h-4" />
            Previous
          </Button>
          
          <span className="text-sm text-gray-500">
            Page {page} of {pagination.pages}
          </span>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => handlePageChange(page + 1)}
            disabled={page >= pagination.pages}
          >
            Next
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
