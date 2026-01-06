import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { Plus, Activity, TrendingUp, Repeat } from 'lucide-react';
import { domainsApi, workoutsApi } from '../api/client';
import { RadarChart, EmptyRadarChart } from '../components/charts/RadarChart';
import { TrendChart } from '../components/charts/TrendChart';
import { Card, CardHeader, MetricCard } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { DomainGrid } from '../components/dashboard/DomainCard';
import { formatEWU, formatDensityPower, formatDate } from '../utils/formatters';
import { useAuthStore } from '../store/authStore';

export function Dashboard() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [trendPeriod, setTrendPeriod] = React.useState<'7d' | '30d' | '90d'>('30d');

  // Fetch radar data
  const { data: radarData, isLoading: radarLoading } = useQuery({
    queryKey: ['radar'],
    queryFn: domainsApi.getRadar,
  });

  // Fetch domain scores
  const { data: domainsData, isLoading: domainsLoading } = useQuery({
    queryKey: ['domains'],
    queryFn: domainsApi.getAll,
  });

  // Fetch trends
  const { data: trendsData, isLoading: trendsLoading } = useQuery({
    queryKey: ['trends', trendPeriod],
    queryFn: () => domainsApi.getTrends(trendPeriod),
  });

  // Fetch recent workouts
  const { data: workoutsData } = useQuery({
    queryKey: ['workouts', 'recent'],
    queryFn: () => workoutsApi.list({ limit: 5 }),
  });

  const hasWorkouts = workoutsData?.workouts?.length > 0;
  const hasRadarData = radarData?.data?.some((d: any) => d.has_data);

  // Calculate quick stats
  const totalEWUThisWeek = trendsData?.total_ewu?.data?.reduce(
    (sum: number, d: any) => sum + d.value,
    0
  ) || 0;
  const avgDensityPower = trendsData?.density_power?.average || 0;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.name?.split(' ')[0]}
          </h1>
          <p className="text-gray-500 mt-1">Track your CrossFit performance</p>
        </div>
        <Button
          onClick={() => navigate('/log')}
          leftIcon={<Plus className="w-5 h-5" />}
        >
          Log Workout
        </Button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <MetricCard
          label="Total EWU This Period"
          value={formatEWU(totalEWUThisWeek, 0)}
          unit="EWU"
          icon={<Activity className="w-5 h-5" />}
        />
        <MetricCard
          label="Avg Density Power"
          value={avgDensityPower.toFixed(2)}
          unit="EWU/min"
          icon={<TrendingUp className="w-5 h-5" />}
        />
        <MetricCard
          label="Workouts Logged"
          value={workoutsData?.pagination?.total || 0}
          icon={<Repeat className="w-5 h-5" />}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Radar Chart */}
        <Card className="lg:col-span-2">
          <CardHeader
            title="Athlete Completeness"
            subtitle="Your performance across 5 domains"
          />
          {radarLoading ? (
            <div className="h-80 flex items-center justify-center">
              <div className="animate-pulse text-gray-400">Loading...</div>
            </div>
          ) : hasRadarData ? (
            <RadarChart data={radarData.data} />
          ) : (
            <EmptyRadarChart />
          )}
        </Card>

        {/* Recent Workouts */}
        <Card>
          <CardHeader
            title="Recent Workouts"
            action={
              hasWorkouts && (
                <Link
                  to="/history"
                  className="text-sm text-primary-600 hover:text-primary-700"
                >
                  View all
                </Link>
              )
            }
          />
          {hasWorkouts ? (
            <div className="space-y-3">
              {workoutsData.workouts.map((workout: any) => (
                <Link
                  key={workout.id}
                  to={`/workout/${workout.id}`}
                  className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">
                        {workout.name || workout.workout_type || 'Workout'}
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatDate(workout.performed_at)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-primary-600">
                        {formatEWU(workout.total_ewu || 0)} EWU
                      </p>
                      {workout.density_power_min && (
                        <p className="text-xs text-gray-500">
                          {workout.density_power_min.toFixed(1)} EWU/min
                        </p>
                      )}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-4">No workouts logged yet</p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/log')}
              >
                Log your first workout
              </Button>
            </div>
          )}
        </Card>
      </div>

      {/* Domain Scores Grid */}
      <Card className="mb-8">
        <CardHeader
          title="Domain Scores"
          subtitle="Click a domain to see details"
        />
        {domainsLoading ? (
          <div className="animate-pulse h-32" />
        ) : (
          <DomainGrid
            domains={domainsData?.domains || []}
            onDomainClick={(domain) => navigate(`/domain/${domain}`)}
          />
        )}
      </Card>

      {/* Trends */}
      <Card>
        <CardHeader
          title="Performance Trends"
          action={
            <div className="flex gap-2">
              {(['7d', '30d', '90d'] as const).map((period) => (
                <button
                  key={period}
                  onClick={() => setTrendPeriod(period)}
                  className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                    trendPeriod === period
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-500 hover:bg-gray-100'
                  }`}
                >
                  {period}
                </button>
              ))}
            </div>
          }
        />
        {trendsLoading ? (
          <div className="animate-pulse h-40" />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <TrendChart
              data={trendsData?.density_power?.data || []}
              title="Density Power"
              unit="EWU/min"
              color="#0ea5e9"
              showArea
            />
            <TrendChart
              data={trendsData?.total_ewu?.data || []}
              title="Total EWU per Workout"
              unit="EWU"
              color="#8b5cf6"
              showArea
            />
          </div>
        )}
      </Card>
    </div>
  );
}
