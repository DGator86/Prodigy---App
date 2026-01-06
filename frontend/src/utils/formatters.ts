/**
 * Format utilities for the CrossFit Performance App
 */

// Format time in seconds to MM:SS or HH:MM:SS
export function formatTime(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

// Format EWU value with precision
export function formatEWU(value: number, precision: number = 1): string {
  return value.toFixed(precision);
}

// Format percentage
export function formatPercent(value: number, precision: number = 1): string {
  return `${(value * 100).toFixed(precision)}%`;
}

// Format density power
export function formatDensityPower(value: number): string {
  return `${value.toFixed(2)} EWU/min`;
}

// Format date for display
export function formatDate(date: string | Date): string {
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

// Format datetime for display
export function formatDateTime(date: string | Date): string {
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

// Get confidence badge color
export function getConfidenceColor(confidence: string): string {
  switch (confidence) {
    case 'high':
      return 'badge-success';
    case 'medium':
      return 'badge-warning';
    case 'low':
      return 'badge-error';
    default:
      return 'badge-info';
  }
}

// Get workout type display name
export function getWorkoutTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    sprint: 'Sprint',
    threshold: 'Threshold',
    endurance: 'Endurance',
    interval: 'Interval',
    chipper: 'Chipper',
    strength: 'Strength',
    monostructural: 'Mono',
  };
  return labels[type] || type;
}

// Get domain display name
export function getDomainLabel(domain: string): string {
  const labels: Record<string, string> = {
    strength_output: 'Strength',
    monostructural_output: 'Monostructural',
    mixed_modal_capacity: 'Mixed-Modal',
    sprint_power_capacity: 'Sprint/Power',
    repeatability: 'Repeatability',
  };
  return labels[domain] || domain;
}

// Movement type display name
export function getMovementLabel(movement: string): string {
  return movement
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// Get modality color
export function getModalityColor(modality: string): string {
  switch (modality) {
    case 'machine':
      return 'text-blue-600';
    case 'lift':
      return 'text-red-600';
    case 'gymnastics':
      return 'text-purple-600';
    default:
      return 'text-gray-600';
  }
}
