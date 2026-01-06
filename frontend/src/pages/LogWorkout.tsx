import React from 'react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { workoutsApi } from '../api/client';
import { Card, CardHeader } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Input, Select, Textarea } from '../components/common/Input';
import { MovementList, MovementData } from '../components/workout/MovementEntry';
import { SplitEntry, SplitData } from '../components/workout/SplitEntry';

const TEMPLATE_OPTIONS = [
  { value: 'interval', label: 'Interval (EMOM/E3MOM)' },
  { value: 'chipper', label: 'Chipper' },
  { value: 'sprint_test', label: 'Sprint Test (<5 min)' },
  { value: 'threshold', label: 'Threshold (5-15 min)' },
  { value: 'endurance', label: 'Endurance (15+ min)' },
  { value: 'strength_session', label: 'Strength Session' },
  { value: 'monostructural_test', label: 'Mono Test (Bike/Row/Run)' },
  { value: 'custom', label: 'Custom' },
];

interface FormData {
  name: string;
  template_type: string;
  total_time_minutes: number;
  total_time_seconds: number;
  round_count: number;
  notes: string;
  movements: MovementData[];
  splits: SplitData[];
  performed_at: string;
}

export function LogWorkout() {
  const navigate = useNavigate();
  const [formData, setFormData] = React.useState<FormData>({
    name: '',
    template_type: 'interval',
    total_time_minutes: 0,
    total_time_seconds: 0,
    round_count: 1,
    notes: '',
    movements: [{ movement_type: '', reps: 1, order_index: 0 }],
    splits: [],
    performed_at: new Date().toISOString().slice(0, 16),
  });
  const [errors, setErrors] = React.useState<Record<string, string>>({});

  const createWorkout = useMutation({
    mutationFn: workoutsApi.create,
    onSuccess: (data) => {
      navigate(`/workout/${data.workout.id}/results`, { state: { data } });
    },
    onError: (error: any) => {
      setErrors({ submit: error.response?.data?.detail || 'Failed to log workout' });
    },
  });

  const handleChange = (field: keyof FormData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: '' }));
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    const totalSeconds =
      formData.total_time_minutes * 60 + formData.total_time_seconds;
    if (totalSeconds <= 0) {
      newErrors.time = 'Total time is required';
    }

    if (formData.movements.length === 0) {
      newErrors.movements = 'At least one movement is required';
    }

    const hasEmptyMovement = formData.movements.some((m) => !m.movement_type);
    if (hasEmptyMovement) {
      newErrors.movements = 'Please select a movement type for all entries';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    const totalSeconds =
      formData.total_time_minutes * 60 + formData.total_time_seconds;

    // Filter out empty splits
    const validSplits = formData.splits.filter((s) => s.time_seconds > 0);

    createWorkout.mutate({
      name: formData.name || null,
      template_type: formData.template_type,
      total_time_seconds: totalSeconds,
      round_count: formData.round_count,
      performed_at: new Date(formData.performed_at).toISOString(),
      notes: formData.notes || null,
      movements: formData.movements.map((m) => ({
        movement_type: m.movement_type,
        reps: m.reps || 1,
        load_lb: m.load_lb || null,
        calories: m.calories || null,
        order_index: m.order_index,
      })),
      splits: validSplits.length > 0 ? validSplits : null,
    });
  };

  const showSplits =
    formData.template_type === 'interval' && formData.round_count > 1;

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <button
          onClick={() => navigate(-1)}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Log Workout</h1>
          <p className="text-gray-500">Record your CrossFit session</p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Template Selection */}
        <Card className="mb-6">
          <CardHeader title="Workout Type" />
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {TEMPLATE_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => handleChange('template_type', option.value)}
                className={`p-3 text-sm rounded-lg border-2 transition-colors ${
                  formData.template_type === option.value
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-gray-200 hover:border-gray-300 text-gray-700'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </Card>

        {/* Basic Info */}
        <Card className="mb-6">
          <CardHeader title="Workout Details" />
          <div className="space-y-4">
            <Input
              label="Workout Name (optional)"
              placeholder="e.g., E3MOM Power Snatch"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
            />

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Total Time</label>
                <div className="flex gap-2">
                  <div className="flex-1">
                    <Input
                      type="number"
                      placeholder="Min"
                      value={formData.total_time_minutes || ''}
                      onChange={(e) =>
                        handleChange('total_time_minutes', parseInt(e.target.value) || 0)
                      }
                      min={0}
                    />
                  </div>
                  <span className="self-center text-gray-500">:</span>
                  <div className="flex-1">
                    <Input
                      type="number"
                      placeholder="Sec"
                      value={formData.total_time_seconds || ''}
                      onChange={(e) =>
                        handleChange('total_time_seconds', parseInt(e.target.value) || 0)
                      }
                      min={0}
                      max={59}
                    />
                  </div>
                </div>
                {errors.time && (
                  <p className="text-sm text-red-600 mt-1">{errors.time}</p>
                )}
              </div>

              <Input
                label="Rounds"
                type="number"
                value={formData.round_count}
                onChange={(e) =>
                  handleChange('round_count', parseInt(e.target.value) || 1)
                }
                min={1}
                max={100}
              />
            </div>

            <Input
              label="Date & Time"
              type="datetime-local"
              value={formData.performed_at}
              onChange={(e) => handleChange('performed_at', e.target.value)}
            />
          </div>
        </Card>

        {/* Movements */}
        <Card className="mb-6">
          <CardHeader
            title="Movements"
            subtitle={
              formData.round_count > 1
                ? `Enter movements for ONE round (will be repeated ${formData.round_count}x)`
                : 'Enter all movements for the workout'
            }
          />
          <MovementList
            movements={formData.movements}
            onChange={(movements) => handleChange('movements', movements)}
          />
          {errors.movements && (
            <p className="text-sm text-red-600 mt-2">{errors.movements}</p>
          )}
        </Card>

        {/* Splits */}
        {showSplits && (
          <Card className="mb-6">
            <CardHeader
              title="Split Times"
              subtitle="Track your time per round for repeatability metrics"
            />
            <SplitEntry
              splits={formData.splits}
              roundCount={formData.round_count}
              onChange={(splits) => handleChange('splits', splits)}
            />
          </Card>
        )}

        {/* Notes */}
        <Card className="mb-6">
          <CardHeader title="Notes (optional)" />
          <Textarea
            placeholder="How did it feel? Any scaling? Equipment notes?"
            value={formData.notes}
            onChange={(e) => handleChange('notes', e.target.value)}
            rows={3}
          />
        </Card>

        {/* Submit */}
        {errors.submit && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {errors.submit}
          </div>
        )}

        <div className="flex gap-4">
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate(-1)}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            isLoading={createWorkout.isPending}
            className="flex-1"
          >
            Log Workout
          </Button>
        </div>
      </form>
    </div>
  );
}
