import React from 'react';
import {
  Radar,
  RadarChart as RechartsRadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

interface RadarDataPoint {
  domain: string;
  label: string;
  score: number | null;
  confidence: string;
  has_data: boolean;
}

interface RadarChartProps {
  data: RadarDataPoint[];
  className?: string;
}

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white px-3 py-2 rounded-lg shadow-lg border border-gray-200">
        <p className="font-semibold text-gray-900">{data.label}</p>
        {data.has_data ? (
          <>
            <p className="text-primary-600 font-medium">
              Score: {data.score?.toFixed(1)}/100
            </p>
            <p className="text-gray-500 text-sm capitalize">
              Confidence: {data.confidence}
            </p>
          </>
        ) : (
          <p className="text-gray-500 text-sm">No data yet</p>
        )}
      </div>
    );
  }
  return null;
};

export function RadarChart({ data, className = '' }: RadarChartProps) {
  // Transform data for Recharts - use 0 for null scores
  const chartData = data.map((d) => ({
    ...d,
    value: d.score ?? 0,
    fullMark: 100,
  }));

  return (
    <div className={`w-full h-80 ${className}`}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsRadarChart data={chartData}>
          <PolarGrid strokeDasharray="3 3" />
          <PolarAngleAxis
            dataKey="label"
            tick={{ fill: '#374151', fontSize: 12 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: '#9ca3af', fontSize: 10 }}
            tickCount={5}
          />
          <Radar
            name="Score"
            dataKey="value"
            stroke="#0ea5e9"
            fill="#0ea5e9"
            fillOpacity={0.3}
            strokeWidth={2}
          />
          <Tooltip content={<CustomTooltip />} />
        </RechartsRadarChart>
      </ResponsiveContainer>
    </div>
  );
}

// Empty state radar for new users
export function EmptyRadarChart({ className = '' }: { className?: string }) {
  const emptyData = [
    { label: 'Strength', value: 0, fullMark: 100 },
    { label: 'Monostructural', value: 0, fullMark: 100 },
    { label: 'Mixed-Modal', value: 0, fullMark: 100 },
    { label: 'Sprint/Power', value: 0, fullMark: 100 },
    { label: 'Repeatability', value: 0, fullMark: 100 },
  ];

  return (
    <div className={`w-full h-80 ${className}`}>
      <ResponsiveContainer width="100%" height="100%">
        <RechartsRadarChart data={emptyData}>
          <PolarGrid strokeDasharray="3 3" />
          <PolarAngleAxis
            dataKey="label"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: '#d1d5db', fontSize: 10 }}
            tickCount={5}
          />
          <Radar
            name="Score"
            dataKey="value"
            stroke="#d1d5db"
            fill="#d1d5db"
            fillOpacity={0.1}
            strokeWidth={1}
            strokeDasharray="5 5"
          />
        </RechartsRadarChart>
      </ResponsiveContainer>
      <p className="text-center text-gray-500 text-sm -mt-4">
        Log workouts to build your athlete profile
      </p>
    </div>
  );
}
