import React from 'react';
import { X } from 'lucide-react';
import { Input, Select } from '../common/Input';
import { Button } from '../common/Button';

// Movement type options
const MACHINE_MOVEMENTS = [
  { value: 'echo_bike', label: 'Echo Bike' },
  { value: 'rower', label: 'Rower' },
  { value: 'ski_erg', label: 'Ski Erg' },
  { value: 'assault_bike', label: 'Assault Bike' },
  { value: 'run', label: 'Run' },
];

const BARBELL_MOVEMENTS = [
  { value: 'power_snatch', label: 'Power Snatch' },
  { value: 'squat_snatch', label: 'Squat Snatch' },
  { value: 'power_clean', label: 'Power Clean' },
  { value: 'squat_clean', label: 'Squat Clean' },
  { value: 'clean_and_jerk', label: 'Clean & Jerk' },
  { value: 'deadlift', label: 'Deadlift' },
  { value: 'back_squat', label: 'Back Squat' },
  { value: 'front_squat', label: 'Front Squat' },
  { value: 'overhead_squat', label: 'Overhead Squat' },
  { value: 'strict_press', label: 'Strict Press' },
  { value: 'push_press', label: 'Push Press' },
  { value: 'push_jerk', label: 'Push Jerk' },
  { value: 'thruster', label: 'Thruster' },
  { value: 'hang_power_snatch', label: 'Hang Power Snatch' },
  { value: 'hang_power_clean', label: 'Hang Power Clean' },
];

const GYMNASTICS_MOVEMENTS = [
  { value: 'pull_up', label: 'Pull-up' },
  { value: 'chest_to_bar', label: 'Chest-to-Bar' },
  { value: 'muscle_up', label: 'Muscle-up' },
  { value: 'bar_muscle_up', label: 'Bar Muscle-up' },
  { value: 'toes_to_bar', label: 'Toes-to-Bar' },
  { value: 'handstand_push_up', label: 'HSPU' },
  { value: 'box_jump', label: 'Box Jump' },
  { value: 'burpee', label: 'Burpee' },
  { value: 'double_under', label: 'Double Under' },
  { value: 'wall_ball', label: 'Wall Ball' },
  { value: 'kettlebell_swing', label: 'KB Swing' },
];

const ALL_MOVEMENTS = [
  { label: '--- Machine ---', value: '', disabled: true },
  ...MACHINE_MOVEMENTS,
  { label: '--- Barbell ---', value: '', disabled: true },
  ...BARBELL_MOVEMENTS,
  { label: '--- Gymnastics ---', value: '', disabled: true },
  ...GYMNASTICS_MOVEMENTS,
];

// Helper to determine if movement is machine type
const isMachineMovement = (type: string) => 
  MACHINE_MOVEMENTS.some(m => m.value === type);

const isBarbellMovement = (type: string) =>
  BARBELL_MOVEMENTS.some(m => m.value === type);

export interface MovementData {
  movement_type: string;
  reps: number;
  load_lb?: number;
  calories?: number;
  order_index: number;
}

interface MovementEntryProps {
  movement: MovementData;
  index: number;
  onChange: (index: number, data: Partial<MovementData>) => void;
  onRemove: (index: number) => void;
  canRemove: boolean;
}

export function MovementEntry({
  movement,
  index,
  onChange,
  onRemove,
  canRemove,
}: MovementEntryProps) {
  const isMachine = isMachineMovement(movement.movement_type);
  const isBarbell = isBarbellMovement(movement.movement_type);

  return (
    <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
      <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="col-span-2">
          <label className="label text-xs">Movement</label>
          <select
            className="input py-1.5 text-sm"
            value={movement.movement_type}
            onChange={(e) => {
              const newType = e.target.value;
              const updates: Partial<MovementData> = { movement_type: newType };
              
              // Reset fields based on movement type
              if (isMachineMovement(newType)) {
                updates.load_lb = undefined;
                updates.reps = 1;
              } else {
                updates.calories = undefined;
              }
              
              onChange(index, updates);
            }}
          >
            <option value="">Select movement...</option>
            {ALL_MOVEMENTS.map((m, i) => (
              <option 
                key={`${m.value}-${i}`} 
                value={m.value} 
                disabled={(m as any).disabled}
              >
                {m.label}
              </option>
            ))}
          </select>
        </div>

        {isMachine ? (
          <div>
            <label className="label text-xs">Calories</label>
            <input
              type="number"
              className="input py-1.5 text-sm"
              value={movement.calories || ''}
              onChange={(e) => onChange(index, { calories: parseInt(e.target.value) || 0 })}
              min={1}
              placeholder="Cal"
            />
          </div>
        ) : (
          <>
            <div>
              <label className="label text-xs">Reps</label>
              <input
                type="number"
                className="input py-1.5 text-sm"
                value={movement.reps || ''}
                onChange={(e) => onChange(index, { reps: parseInt(e.target.value) || 0 })}
                min={1}
                placeholder="Reps"
              />
            </div>
            {isBarbell && (
              <div>
                <label className="label text-xs">Load (lb)</label>
                <input
                  type="number"
                  className="input py-1.5 text-sm"
                  value={movement.load_lb || ''}
                  onChange={(e) => onChange(index, { load_lb: parseFloat(e.target.value) || 0 })}
                  min={0}
                  step={5}
                  placeholder="lb"
                />
              </div>
            )}
          </>
        )}
      </div>

      {canRemove && (
        <button
          type="button"
          onClick={() => onRemove(index)}
          className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded mt-5"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}

interface MovementListProps {
  movements: MovementData[];
  onChange: (movements: MovementData[]) => void;
}

export function MovementList({ movements, onChange }: MovementListProps) {
  const handleChange = (index: number, data: Partial<MovementData>) => {
    const updated = [...movements];
    updated[index] = { ...updated[index], ...data };
    onChange(updated);
  };

  const handleRemove = (index: number) => {
    const updated = movements.filter((_, i) => i !== index);
    // Update order indices
    updated.forEach((m, i) => (m.order_index = i));
    onChange(updated);
  };

  const handleAdd = () => {
    onChange([
      ...movements,
      {
        movement_type: '',
        reps: 1,
        order_index: movements.length,
      },
    ]);
  };

  return (
    <div className="space-y-3">
      {movements.map((movement, index) => (
        <MovementEntry
          key={index}
          movement={movement}
          index={index}
          onChange={handleChange}
          onRemove={handleRemove}
          canRemove={movements.length > 1}
        />
      ))}
      
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={handleAdd}
        className="w-full"
      >
        + Add Movement
      </Button>
    </div>
  );
}
