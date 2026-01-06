import React from 'react';
import { Clock } from 'lucide-react';

export interface SplitData {
  round_number: number;
  time_seconds: number;
}

interface SplitEntryProps {
  splits: SplitData[];
  roundCount: number;
  onChange: (splits: SplitData[]) => void;
}

export function SplitEntry({ splits, roundCount, onChange }: SplitEntryProps) {
  // Ensure we have the right number of split entries
  React.useEffect(() => {
    if (roundCount <= 1) {
      onChange([]);
      return;
    }

    const newSplits: SplitData[] = [];
    for (let i = 1; i <= roundCount; i++) {
      const existing = splits.find((s) => s.round_number === i);
      newSplits.push({
        round_number: i,
        time_seconds: existing?.time_seconds || 0,
      });
    }
    
    if (JSON.stringify(newSplits) !== JSON.stringify(splits)) {
      onChange(newSplits);
    }
  }, [roundCount]);

  const handleChange = (roundNumber: number, timeSeconds: number) => {
    const updated = splits.map((s) =>
      s.round_number === roundNumber ? { ...s, time_seconds: timeSeconds } : s
    );
    onChange(updated);
  };

  // Parse time input (MM:SS or just seconds)
  const parseTimeInput = (value: string): number => {
    if (value.includes(':')) {
      const [min, sec] = value.split(':').map(Number);
      return (min || 0) * 60 + (sec || 0);
    }
    return parseInt(value) || 0;
  };

  // Format seconds to MM:SS
  const formatTime = (seconds: number): string => {
    if (seconds === 0) return '';
    const min = Math.floor(seconds / 60);
    const sec = seconds % 60;
    return `${min}:${sec.toString().padStart(2, '0')}`;
  };

  if (roundCount <= 1) {
    return null;
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <Clock className="w-4 h-4" />
        <span>Split Times (optional but recommended)</span>
      </div>
      
      <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2">
        {splits.map((split) => (
          <div key={split.round_number}>
            <label className="label text-xs text-center">
              Round {split.round_number}
            </label>
            <input
              type="text"
              className="input py-1.5 text-sm text-center"
              placeholder="M:SS"
              value={formatTime(split.time_seconds)}
              onChange={(e) => {
                const seconds = parseTimeInput(e.target.value);
                handleChange(split.round_number, seconds);
              }}
              onBlur={(e) => {
                // Reformat on blur
                const seconds = parseTimeInput(e.target.value);
                if (seconds > 0) {
                  e.target.value = formatTime(seconds);
                }
              }}
            />
          </div>
        ))}
      </div>
      
      <p className="text-xs text-gray-500">
        Enter time as MM:SS (e.g., 1:30) or just seconds (e.g., 90).
        Split times enable repeatability metrics.
      </p>
    </div>
  );
}

// Quick split time calculator
export function SplitCalculator({
  totalTime,
  roundCount,
  onApply,
}: {
  totalTime: number;
  roundCount: number;
  onApply: (splits: SplitData[]) => void;
}) {
  const [strategy, setStrategy] = React.useState<'even' | 'descending' | 'custom'>('even');
  
  const calculateSplits = () => {
    if (roundCount <= 1 || totalTime <= 0) return;
    
    const splits: SplitData[] = [];
    
    if (strategy === 'even') {
      // Even splits
      const splitTime = Math.round(totalTime / roundCount);
      for (let i = 1; i <= roundCount; i++) {
        splits.push({ round_number: i, time_seconds: splitTime });
      }
    } else if (strategy === 'descending') {
      // Negative splits (getting faster)
      const baseSplit = totalTime / roundCount;
      const decrement = baseSplit * 0.05; // 5% faster each round
      
      for (let i = 1; i <= roundCount; i++) {
        const time = Math.round(baseSplit - (i - 1) * decrement);
        splits.push({ round_number: i, time_seconds: Math.max(time, 30) });
      }
    }
    
    onApply(splits);
  };

  if (roundCount <= 1) return null;

  return (
    <div className="flex items-center gap-2 mt-2">
      <select
        className="input py-1 text-sm w-auto"
        value={strategy}
        onChange={(e) => setStrategy(e.target.value as any)}
      >
        <option value="even">Even splits</option>
        <option value="descending">Negative splits</option>
      </select>
      <button
        type="button"
        onClick={calculateSplits}
        className="text-sm text-primary-600 hover:text-primary-700"
      >
        Auto-fill
      </button>
    </div>
  );
}
