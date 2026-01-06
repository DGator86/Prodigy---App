import React from 'react';
import { useMutation } from '@tanstack/react-query';
import { Download, FileJson, FileSpreadsheet } from 'lucide-react';
import { exportApi } from '../api/client';
import { Card, CardHeader } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';

export function Export() {
  const [startDate, setStartDate] = React.useState('');
  const [endDate, setEndDate] = React.useState('');
  const [includeDistributions, setIncludeDistributions] = React.useState(false);

  const exportCsv = useMutation({
    mutationFn: () =>
      exportApi.csv({
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      }),
    onSuccess: (data) => {
      // Create download link
      const url = window.URL.createObjectURL(new Blob([data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute(
        'download',
        `crossfit_export_${new Date().toISOString().split('T')[0]}.csv`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
    },
  });

  const exportJson = useMutation({
    mutationFn: () =>
      exportApi.json({
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        include_distributions: includeDistributions,
      }),
    onSuccess: (data) => {
      // Create download link
      const json = JSON.stringify(data, null, 2);
      const url = window.URL.createObjectURL(
        new Blob([json], { type: 'application/json' })
      );
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute(
        'download',
        `crossfit_export_${new Date().toISOString().split('T')[0]}.json`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
    },
  });

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Export Data</h1>
        <p className="text-gray-500 mt-1">
          Download your workout data in CSV or JSON format
        </p>
      </div>

      {/* Date Range Filter */}
      <Card className="mb-6">
        <CardHeader
          title="Date Range (Optional)"
          subtitle="Leave empty to export all data"
        />
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Start Date"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
          <Input
            label="End Date"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </div>
      </Card>

      {/* Export Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* CSV Export */}
        <Card>
          <div className="text-center">
            <FileSpreadsheet className="w-12 h-12 text-green-500 mx-auto mb-4" />
            <h3 className="font-semibold text-lg text-gray-900 mb-2">
              Export as CSV
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              Spreadsheet format compatible with Excel, Google Sheets, etc.
            </p>
            <p className="text-xs text-gray-400 mb-4">
              Includes: workout details, computed metrics, timestamps
            </p>
            <Button
              onClick={() => exportCsv.mutate()}
              isLoading={exportCsv.isPending}
              leftIcon={<Download className="w-4 h-4" />}
              className="w-full"
            >
              Download CSV
            </Button>
          </div>
        </Card>

        {/* JSON Export */}
        <Card>
          <div className="text-center">
            <FileJson className="w-12 h-12 text-blue-500 mx-auto mb-4" />
            <h3 className="font-semibold text-lg text-gray-900 mb-2">
              Export as JSON
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              Full data export including movements, splits, and domain scores
            </p>
            
            <label className="flex items-center justify-center gap-2 text-sm text-gray-600 mb-4">
              <input
                type="checkbox"
                checked={includeDistributions}
                onChange={(e) => setIncludeDistributions(e.target.checked)}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              Include distribution data
            </label>
            
            <Button
              onClick={() => exportJson.mutate()}
              isLoading={exportJson.isPending}
              leftIcon={<Download className="w-4 h-4" />}
              className="w-full"
            >
              Download JSON
            </Button>
          </div>
        </Card>
      </div>

      {/* Data Info */}
      <Card className="mt-6">
        <CardHeader title="Your Data, Your Control" />
        <div className="prose prose-sm text-gray-600">
          <p>
            Your workout data belongs to you. Export it anytime to:
          </p>
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>Create backups of your training history</li>
            <li>Analyze your data with other tools</li>
            <li>Transfer to another platform</li>
            <li>Share with your coach</li>
          </ul>
          <p className="mt-4 text-xs text-gray-400">
            JSON exports include complete workout data with all metrics,
            movements, splits, and domain scores. CSV exports are optimized
            for spreadsheet analysis.
          </p>
        </div>
      </Card>
    </div>
  );
}
